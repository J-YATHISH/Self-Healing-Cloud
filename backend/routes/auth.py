from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import Optional
import json
import base64
import secrets
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from firebase_admin import firestore
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.agent import db
    from services.credential_manager import store_credentials
except ImportError as e:
    print(f"Import error: {e}")
    db = None

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth configuration
SCOPES = [
    "openid",  # Required for ID token
    "https://www.googleapis.com/auth/userinfo.email",  # Get email
    "https://www.googleapis.com/auth/userinfo.profile",  # Get name
    "https://www.googleapis.com/auth/logging.read",
    "https://www.googleapis.com/auth/cloud-platform.read-only",
]

REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), '..', 'client_secret.json')

class AuthRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(creds: AuthRequest):
    """Mock login endpoint"""
    return {"token": "mock-jwt-token-xyz", "user": {"id": 1, "name": "SRE User"}}

@router.post("/demo/login")
async def demo_login():
    """Bypass logic for 'Test Account with Real GCP Deployment'"""
    if os.getenv("DEMO_MODE") != "true":
        raise HTTPException(status_code=403, detail="Demo mode is disabled.")
    
    # Real account details provided by user
    user_name = "Jaiganesh S"
    user_email = "s.jaiganesh1607@gmail.com"
    user_id = "101164602584260907344" # Actual User ID in Firestore
    project_id = "project-e2bcb697-e160-439a-a3c"
    
    user_data = {
        'user_id': user_id,
        'email': user_email,
        'name': user_name,
        'projectId': project_id
    }
    
    # Generate session token
    import json
    import base64
    session_token = base64.b64encode(json.dumps(user_data).encode()).decode()
    
    return {
        "token": session_token,
        "user": {
            "id": user_id,
            "name": user_name,
            "email": user_email,
            "projectId": project_id
        }
    }

@router.get("/status")
async def auth_status():
    """Check authentication status"""
    return {"authenticated": True, "user": "SRE User"}

@router.post("/setup")
async def auth_setup():
    """Initial authentication setup"""
    return {"status": "Setup Complete"}


# OAuth endpoints
@router.get("/google/authorize")
async def google_authorize(project_id: Optional[str] = None):
    """
    Generate Google OAuth authorization URL
    Includes project_id in state to preserve it through the flow
    Returns authorization URL for user to visit
    """
    try:
        import json
        import base64
        import secrets

        if not os.path.exists(CLIENT_SECRETS_FILE):
            raise HTTPException(
                status_code=500,
                detail=f"client_secret.json not found at {CLIENT_SECRETS_FILE}"
            )
        
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        # Custom state to carry project_id
        csrf_state = secrets.token_urlsafe(16)
        state_data = {
            "csrf": csrf_state,
            "project_id": project_id
        }
        state_str = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()

        authorization_url, _ = flow.authorization_url(
            state=state_str,
            access_type='offline',
            prompt='consent'  # Force consent to get refresh_token
        )
        
        return {
            "authorization_url": authorization_url,
            "state": state_str
        }
    except Exception as e:
        print(f"❌ OAuth authorize error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...), 
    state: str = Query(...)
):
    """
    Handle OAuth callback from Google
    Exchanges authorization code for tokens and stores credentials
    
    Note: project_id should be stored in frontend sessionStorage
    and sent in subsequent API calls, not in OAuth callback
    """
    print(f"🔍 OAuth callback received - code: {code[:20]}...")
    
    # Extract project_id from encoded state
    project_id = None
    try:
        import json
        import base64
        state_data = json.loads(base64.urlsafe_b64decode(state).decode())
        project_id = state_data.get("project_id")
        print(f"📋 Extracted project_id from state: {project_id}")
    except Exception as e:
        print(f"⚠️ Failed to decode state: {e}")
        
    try:
        if db is None:
            raise HTTPException(status_code=503, detail="Firebase not initialized")
        
        # Create flow with same parameters
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=state
        )
        
        # Exchange authorization code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Extract user info from ID token or userinfo endpoint
        import google.auth.transport.requests
        from google.oauth2 import id_token
        import requests as http_requests
        
        user_email = "unknown@example.com"
        user_name = "Unknown User"
        user_id = "default_user"
        
        try:
            # Try to get info from ID token first
            if credentials.id_token:
                request = google.auth.transport.requests.Request()
                id_info = id_token.verify_oauth2_token(
                    credentials.id_token,
                    request,
                    credentials.client_id
                )
                user_email = id_info.get('email', 'unknown@example.com')
                user_name = id_info.get('name', user_email.split('@')[0])
                user_id = id_info.get('sub')  # Google's unique user ID
                print(f"✅ Extracted user info from ID token")
            else:
                # Fallback: Use userinfo endpoint
                print(f"⚠️ No ID token, using userinfo endpoint")
                userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
                headers = {'Authorization': f'Bearer {credentials.token}'}
                response = http_requests.get(userinfo_url, headers=headers)
                
                if response.status_code == 200:
                    userinfo = response.json()
                    user_email = userinfo.get('email', 'unknown@example.com')
                    user_name = userinfo.get('name', user_email.split('@')[0])
                    user_id = userinfo.get('id', 'default_user')
                    print(f"✅ Extracted user info from userinfo endpoint")
                else:
                    print(f"❌ Failed to get userinfo: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Failed to extract user info: {e}")
        
        print(f"✅ User authenticated: {user_name} ({user_email}), ID: {user_id}")
        
        # Store credentials in Firestore with user ID and project_id
        print(f"💾 Storing credentials for user {user_id} with project_id: {project_id}")
        await store_credentials(db, user_id, credentials, project_id)
        
        # Store user profile
        await db.collection('users').document(user_id).set({
            'email': user_email,
            'name': user_name,
            'project_id': project_id,  # Store project ID in user profile
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_login': firestore.SERVER_TIMESTAMP
        }, merge=True)
        
        # Generate session token with user info
        import json
        import base64
        user_data = {
            'user_id': user_id,
            'email': user_email,
            'name': user_name,
            'projectId': project_id  # Include project_id in token
        }
        session_token = base64.b64encode(json.dumps(user_data).encode()).decode()
        
        print(f"🎫 Generated session token for {user_name}")
        print(f"🔄 Redirecting to: {FRONTEND_URL}/auth/success?token={session_token[:50]}...")
        
        # Redirect to frontend with success and user data
        redirect_url = f"{FRONTEND_URL}/auth/success?token={session_token}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        # Redirect to frontend with error
        error_url = f"{FRONTEND_URL}/auth?error=oauth_failed&message={str(e)}"
        return RedirectResponse(url=error_url)


@router.get("/google/status")
async def google_auth_status(user_id: str = "default_user"):
    """Check if user has valid Google credentials"""
    try:
        if db is None:
            return {"authenticated": False, "error": "Firebase not initialized"}
        
        doc = await db.collection('user_credentials').document(user_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            return {
                "authenticated": True,
                "user_id": user_id,
                "last_used": data.get('last_used'),
                "created_at": data.get('created_at')
            }
        else:
            return {"authenticated": False, "user_id": user_id}
            
    except Exception as e:
        return {"authenticated": False, "error": str(e)}
