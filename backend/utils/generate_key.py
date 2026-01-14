from cryptography.fernet import Fernet

# Generate a new encryption key
key = Fernet.generate_key()
print("\n" + "="*60)
print("GENERATED ENCRYPTION KEY")
print("="*60)
print("\nAdd this to your backend/.env file:\n")
print(f"CREDENTIAL_ENCRYPTION_KEY={key.decode()}")
print("\n" + "="*60)
