import os
import sys

# Add root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import init_firebase

def list_users():
    db = init_firebase()
    if not db:
        print("❌ Firebase Failed to initialize")
        return
    
    print("👥 Listing users in 'user_credentials' collection:")
    docs = db.collection('user_credentials').stream()
    found = False
    for doc in docs:
        found = True
        print(f"   - {doc.id}")
        data = doc.to_dict()
        print(f"     Project ID: {data.get('project_id')}")
        print(f"     Encrypted: {data.get('encrypted')}")
    
    if not found:
        print("⚠️ No users found in 'user_credentials' collection.")

if __name__ == "__main__":
    list_users()
