"""
Credential Manager for OAuth Token Storage and Retrieval

Handles encryption, storage, and retrieval of Google OAuth credentials
in Firestore with automatic token refresh.
"""
import os
import json
from datetime import datetime
from typing import Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from cryptography.fernet import Fernet
from firebase_admin import firestore

# Load encryption key from environment
ENCRYPTION_KEY = os.getenv('CREDENTIAL_ENCRYPTION_KEY')

# Initialize cipher if key exists
cipher = None
if ENCRYPTION_KEY:
    cipher = Fernet(ENCRYPTION_KEY.encode())
else:
    print("⚠️ WARNING: CREDENTIAL_ENCRYPTION_KEY not set. Credentials will not be encrypted!")


async def store_credentials(db, user_id: str, credentials: Credentials, project_id: Optional[str] = None) -> None:
    """
    Store encrypted OAuth credentials in Firestore
    
    Args:
        db: Firestore client
        user_id: Unique user identifier
        credentials: Google OAuth credentials object
        project_id: GCP Project ID (optional)
    """
    creds_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': list(credentials.scopes) if credentials.scopes else [],
        'expiry': credentials.expiry.isoformat() if credentials.expiry else None
    }
    
    # Encrypt sensitive data if cipher available
    if cipher:
        encrypted_data = cipher.encrypt(json.dumps(creds_dict).encode())
        data_to_store = {
            'encrypted_credentials': encrypted_data.decode(),
            'encrypted': True
        }
    else:
        # Store unencrypted (development only)
        data_to_store = {
            'credentials': creds_dict,
            'encrypted': False
        }
    
    # Add metadata
    data_to_store.update({
        'created_at': firestore.SERVER_TIMESTAMP,
        'last_used': firestore.SERVER_TIMESTAMP,
        'user_id': user_id,
        'project_id': project_id  # Store project ID
    })
    
    await db.collection('user_credentials').document(user_id).set(data_to_store, merge=True)
    print(f"✅ Stored credentials for user: {user_id}")


async def get_credentials(db, user_id: str) -> Optional[Credentials]:
    """
    Retrieve and decrypt user credentials from Firestore
    
    Args:
        db: Firestore client
        user_id: Unique user identifier
        
    Returns:
        Google OAuth Credentials object or None if not found
        
    Raises:
        ValueError: If credentials not found or decryption fails
    """
    doc_ref = db.collection('user_credentials').document(user_id)
    doc = await doc_ref.get()
    
    if not doc.exists:
        raise ValueError(f"No credentials found for user: {user_id}")
    
    data = doc.to_dict()
    project_id = data.get('project_id')
    
    # Decrypt or retrieve credentials
    if data.get('encrypted', False):
        if not cipher:
            raise ValueError("Cannot decrypt credentials: CREDENTIAL_ENCRYPTION_KEY not set")
        
        encrypted_data = data['encrypted_credentials']
        decrypted = cipher.decrypt(encrypted_data.encode())
        creds_dict = json.loads(decrypted)
    else:
        creds_dict = data['credentials']
    
    # Reconstruct expiry datetime
    expiry = None
    if creds_dict.get('expiry'):
        try:
            expiry = datetime.fromisoformat(creds_dict['expiry'])
        except Exception:
            expiry = None

    # Reconstruct Credentials object
    credentials = Credentials(
        token=creds_dict['token'],
        refresh_token=creds_dict['refresh_token'],
        token_uri=creds_dict['token_uri'],
        client_id=creds_dict['client_id'],
        client_secret=creds_dict['client_secret'],
        scopes=creds_dict['scopes'],
        expiry=expiry
    )
    
    # Refresh if expired
    if credentials.expired and credentials.refresh_token:
        print(f"🔄 Refreshing expired token for user: {user_id}")
        try:
            credentials.refresh(Request())
            # Update stored credentials with new token, preserving project_id
            await store_credentials(db, user_id, credentials, project_id=project_id)
            print(f"✅ Token refreshed successfully for project: {project_id}")
        except Exception as e:
            print(f"❌ Failed to refresh token: {e}")
            raise ValueError(f"Failed to refresh credentials: {e}")
    
    # Update last_used timestamp
    await doc_ref.update({'last_used': firestore.SERVER_TIMESTAMP})
    
    return credentials


async def delete_credentials(db, user_id: str) -> bool:
    """
    Delete user credentials from Firestore
    
    Args:
        db: Firestore client
        user_id: Unique user identifier
        
    Returns:
        True if deleted, False if not found
    """
    try:
        await db.collection('user_credentials').document(user_id).delete()
        print(f"🗑️ Deleted credentials for user: {user_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to delete credentials: {e}")
        return False


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key
    
    Returns:
        Base64-encoded encryption key as string
    """
    key = Fernet.generate_key()
    return key.decode()


if __name__ == "__main__":
    # Generate encryption key for .env
    print("Generated Encryption Key (add to .env):")
    print(f"CREDENTIAL_ENCRYPTION_KEY={generate_encryption_key()}")
