"""
Credential Manager for LMS Explorer
Handles secure storage and retrieval of passwords and sensitive data
"""

import os
import sys
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json


class CredentialManager:
    """Manages secure storage of credentials"""
    
    def __init__(self):
        self.key_file = os.path.join(os.path.dirname(__file__), '.credential_key')
        self.credentials_file = os.path.join(os.path.dirname(__file__), '.credentials')
        self._encryption_key = None
        self._fernet = None
        
    def _get_encryption_key(self, password: str = None) -> bytes:
        """Generate or retrieve encryption key"""
        if password is None:
            # Use machine-specific key generation
            password = self._get_machine_specific_key()
        
        # Generate key from password
        password_bytes = password.encode()
        salt = b'lms_explorer_salt'  # In production, use random salt per installation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def _get_machine_specific_key(self) -> str:
        """Generate a machine-specific key for encryption"""
        try:
            # Try to get machine-specific identifiers
            import platform
            import uuid
            
            # Combine machine identifiers
            machine_id = str(uuid.getnode())  # MAC address based
            system_info = platform.system() + platform.release()
            username = os.getlogin() if hasattr(os, 'getlogin') else 'default'
            
            # Create a unique key for this machine
            combined = f"{machine_id}_{system_info}_{username}"
            return hashlib.sha256(combined.encode()).hexdigest()[:32]
            
        except Exception:
            # Fallback to a simple key
            return "lms_explorer_default_key"
    
    def _initialize_encryption(self, password: str = None):
        """Initialize encryption with the given key"""
        if self._fernet is None:
            self._encryption_key = self._get_encryption_key(password)
            self._fernet = Fernet(self._encryption_key)
    
    def encrypt_password(self, password: str, master_password: str = None) -> str:
        """Encrypt a password for storage"""
        self._initialize_encryption(master_password)
        encrypted = self._fernet.encrypt(password.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_password(self, encrypted_password: str, master_password: str = None) -> str:
        """Decrypt a password from storage"""
        try:
            self._initialize_encryption(master_password)
            encrypted_bytes = base64.b64decode(encrypted_password.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            print(f"Error decrypting password: {e}")
            return ""
    
    def save_credentials(self, service_name: str, username: str, password: str, 
                        remember: bool = True, master_password: str = None):
        """Save credentials securely"""
        if not remember:
            # If not remembering, just return without saving
            return
        
        credentials = {}
        
        # Load existing credentials if file exists
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    credentials = json.load(f)
            except (json.JSONDecodeError, IOError):
                credentials = {}
        
        # Encrypt the password
        encrypted_password = self.encrypt_password(password, master_password)
        
        # Store the credentials
        credentials[service_name] = {
            'username': username,
            'password': encrypted_password,
            'remember': remember
        }
        
        # Save to file
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f, indent=2)
        except IOError as e:
            print(f"Error saving credentials: {e}")
    
    def get_credentials(self, service_name: str, master_password: str = None) -> dict:
        """Retrieve credentials for a service"""
        if not os.path.exists(self.credentials_file):
            return {}
        
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            
            if service_name in credentials:
                cred_data = credentials[service_name]
                if cred_data.get('remember', False):
                    # Decrypt the password
                    decrypted_password = self.decrypt_password(
                        cred_data['password'], master_password
                    )
                    return {
                        'username': cred_data['username'],
                        'password': decrypted_password,
                        'remember': True
                    }
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading credentials: {e}")
        
        return {}
    
    def delete_credentials(self, service_name: str):
        """Delete credentials for a service"""
        if not os.path.exists(self.credentials_file):
            return
        
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            
            if service_name in credentials:
                del credentials[service_name]
                
                with open(self.credentials_file, 'w') as f:
                    json.dump(credentials, f, indent=2)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error deleting credentials: {e}")
    
    def list_services(self) -> list:
        """List all services with stored credentials"""
        if not os.path.exists(self.credentials_file):
            return []
        
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            return list(credentials.keys())
        except (json.JSONDecodeError, IOError):
            return []
    
    def clear_all_credentials(self):
        """Clear all stored credentials"""
        if os.path.exists(self.credentials_file):
            try:
                os.remove(self.credentials_file)
            except IOError as e:
                print(f"Error clearing credentials: {e}")


# Global credential manager instance
_credential_manager = None

def get_credential_manager() -> CredentialManager:
    """Get the global credential manager instance"""
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    return _credential_manager
