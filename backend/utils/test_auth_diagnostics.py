import os
import sys
import json
from datetime import datetime

# Add root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import init_firebase
from credential_manager import get_credentials
from google.cloud import logging_v2

def run_diagnostics(user_id="101164602584260907344"):
    print(f"🔍 Starting Diagnostics for user: {user_id}")
    
    # 1. Init Firebase
    db = init_firebase()
    if not db:
        print("❌ Firebase Failed to initialize")
        return
    
    # 2. Get Credentials
    try:
        creds = get_credentials(db, user_id)
        if not creds:
            print(f"❌ No credentials found for {user_id}")
            return
        
        print(f"✅ Credentials retrieved")
        print(f"   - Token exists: {bool(creds.token)}")
        if creds.token:
            print(f"   - Token starts with: {creds.token[:20]}...")
            # Check if it looks like a JWT (ID token)
            if creds.token.count('.') == 2:
                print("   - ⚠️ WARNING: Token looks like a JWT (ID Token). Logging API expects an Access Token.")
                try:
                    import base64
                    header, payload, signature = creds.token.split('.')
                    decoded_payload = json.loads(base64.urlsafe_b64decode(payload + '==').decode())
                    print(f"   - JWT Payload: {json.dumps(decoded_payload, indent=2)}")
                except Exception as e:
                    print(f"   - Failed to decode JWT: {e}")
            else:
                print("   - Token does NOT look like a JWT (this is good for Logging API).")
        
        print(f"   - Expired: {creds.expired}")
        if creds.expiry:
            print(f"   - Expiry: {creds.expiry}")
            
        cred_doc = db.collection('user_credentials').document(user_id).get()
        project_id = cred_doc.to_dict().get('project_id')
        print(f"   - Project ID: {project_id}")
        print(f"   - Scopes: {creds.scopes}")
        
    except Exception as e:
        print(f"❌ Error retrieving credentials: {e}")
        return

    # 3. Test Logging API (Minimal call)
    try:
        print(f"\n📡 Attempting minimal Logging API call for project: {project_id}...")
        client = logging_v2.Client(project=project_id, credentials=creds)
        
        # Just try to list one entry to verify auth
        entries = client.list_entries(page_size=1)
        # Convert to list to trigger the call
        next(iter(entries), None)
        print("✅ SUCCESS: Logging API call completed via Client Library.")
        
    except Exception as e:
        print(f"❌ Logging API Client Library Failed: {e}")
        
        # 4. Try raw HTTP request as fallback diagnostics
        print("\n🌐 Attempting raw HTTP request to Logging API...")
        try:
            import requests
            url = f"https://logging.googleapis.com/v2/entries:list"
            headers = {
                "Authorization": f"Bearer {creds.token}",
                "Content-Type": "application/json"
            }
            payload = {
                "resourceNames": [f"projects/{project_id}"],
                "pageSize": 1
            }
            response = requests.post(url, headers=headers, json=payload)
            print(f"   HTTP Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ SUCCESS: Raw HTTP request succeeded! The issue is likely in the Client Library configuration.")
            else:
                print(f"❌ Raw HTTP request failed: {response.text}")
        except Exception as http_e:
            print(f"❌ Raw HTTP request error: {http_e}")

    # 5. Try fresh credentials flow (Manual/Standalone style)
    print("\n🔄 Comparing with fresh credentials flow (InstalledAppFlow)...")
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        SCOPES = [
            "https://www.googleapis.com/auth/logging.read",
            "https://www.googleapis.com/auth/cloud-platform.read-only",
        ]
        # Note: This might require local server or manually pasting code
        # We'll just check if we can initialize the flow
        flow = InstalledAppFlow.from_client_secrets_file(
            "backend/client_secret.json",
            scopes=SCOPES
        )
        print("✅ Flow initialized successfully from client_secret.json")
    except Exception as flow_e:
        print(f"❌ Flow initialization failed: {flow_e}")

if __name__ == "__main__":
    run_diagnostics()
