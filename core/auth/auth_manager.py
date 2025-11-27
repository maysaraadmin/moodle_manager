"""
Enhanced Authentication Manager for Moodle Manager
Provides secure credential storage, token management, and session handling
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import os
import json
import keyring
import hashlib
import base64
from typing import Dict, Optional, Any, Tuple, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class AuthManager:
    """Enhanced authentication manager with secure credential storage"""
    
    def __init__(self, app_name: str = "MoodleManager"):
        self.app_name = app_name
        self.encryption_key = None
        self.cipher_suite = None
        self.credentials_cache = {}
        self.session_data = {}
        self.token_refresh_threshold = timedelta(hours=1)
        
        # Initialize encryption
        
        # Load cached credentials
        self._load_cached_credentials()
    
    def _initialize_encryption(self):
        """Initialize encryption for secure credential storage with enhanced security"""
        try:
            # Try to get existing encryption key from keyring
            key_data = keyring.get_password(self.app_name, "encryption_key")
            
            if key_data:
                # Validate the key
                try:
                    self.encryption_key = key_data.encode()
                    # Test the key
                    test_cipher = Fernet(self.encryption_key)
                    test_cipher.encrypt(b"test")
                    self.cipher_suite = test_cipher
                    logger.info("Existing encryption key validated successfully")
                except Exception as e:
                    logger.warning(f"Invalid encryption key found, generating new one: {e}")
                    self._generate_and_store_new_key()
            else:
                # Generate new encryption key
                self._generate_and_store_new_key()
            
            logger.info("Encryption initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            # Fallback to in-memory key (less secure)
            self.encryption_key = Fernet.generate_key()
            self.cipher_suite = Fernet(self.encryption_key)
            logger.warning("Using fallback in-memory encryption key")
    
    def _generate_and_store_new_key(self):
        """Generate and store a new encryption key"""
        self.encryption_key = Fernet.generate_key()
        # Store the key securely
        keyring.set_password(self.app_name, "encryption_key", self.encryption_key.decode())
        self.cipher_suite = Fernet(self.encryption_key)
        logger.info("New encryption key generated and stored securely")
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.cipher_suite:
            # Fallback to base64 encoding
            return base64.b64encode(data.encode()).decode()
        
        try:
            encrypted = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return base64.b64encode(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.cipher_suite:
            # Fallback to base64 decoding
            return base64.b64decode(encrypted_data.encode()).decode()
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            try:
                # Try fallback to base64
                return base64.b64decode(encrypted_data.encode()).decode()
            except:
                return ""
    
    def _get_credential_service_name(self, host: str, username: str) -> str:
        """Generate unique service name for credential storage"""
        # Create a hash of the host to avoid long service names
        host_hash = hashlib.md5(host.encode()).hexdigest()[:8]
        return f"{self.app_name}_{host_hash}_{username}"
    
    def store_credentials(self, host: str, username: str, password: str, 
                         service: str = "moodle_mobile_app", remember_me: bool = False) -> bool:
        """Securely store user credentials with enhanced validation and security"""
        try:
            # Validate inputs
            if not self._validate_credential_inputs(host, username, password, service):
                return False
            
            # Check if credentials already exist
            existing_creds = self.get_credentials(host, username)
            if existing_creds:
                logger.warning(f"Credentials already exist for {username}@{host}, updating...")
            
            # Encrypt sensitive data
            encrypted_password = self._encrypt_data(password)
            
            # Create enhanced credential data with security metadata
            credential_data = {
                'username': username,
                'password': encrypted_password,
                'service': service,
                'host': host,
                'remember_me': remember_me,
                'created_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'version': '2.0',  # Credential format version
                'security_level': 'high',
                'device_fingerprint': self._get_device_fingerprint()
            }
            
            # Store in keyring with enhanced service name
            service_name = self._get_credential_service_name(host, username)
            credential_json = json.dumps(credential_data, separators=(',', ':'))  # Compact JSON
            keyring.set_password(service_name, "credentials", credential_json)
            
            # Update cache
            cache_key = f"{host}_{username}"
            self.credentials_cache[cache_key] = credential_data
            
            # Log security event
            logger.info(f"Credentials stored securely for {username}@{host} (security_level: high)")
            
            # Trigger security audit
            self._audit_credential_storage(cache_key, 'store')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
            return False
    
    def get_credentials(self, host: str, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored credentials"""
        try:
            # Check cache first
            cache_key = f"{host}_{username}"
            if cache_key in self.credentials_cache:
                return self.credentials_cache[cache_key]
            
            # Retrieve from keyring
            service_name = self._get_credential_service_name(host, username)
            credential_json = keyring.get_password(service_name, "credentials")
            
            if not credential_json:
                return None
            
            # Parse and decrypt
            credential_data = json.loads(credential_json)
            credential_data['password'] = self._decrypt_data(credential_data['password'])
            
            # Update cache and last used time
            self.credentials_cache[cache_key] = credential_data
            credential_data['last_used'] = datetime.now().isoformat()
            self.store_credentials(host, username, credential_data['password'], 
                                  credential_data.get('service', 'moodle_mobile_app'), 
                                  credential_data.get('remember_me', False))
            
            return credential_data
            
        except Exception as e:
            logger.error(f"Error retrieving credentials: {e}")
            return None
    
    def get_password(self, host: str, username: str) -> Optional[str]:
        """Get password for specific host and username"""
        credentials = self.get_credentials(host, username)
        if credentials:
            return credentials.get('password')
        return None
    
    def get_service(self, host: str, username: str) -> Optional[str]:
        """Get service for specific host and username"""
        credentials = self.get_credentials(host, username)
        if credentials:
            return credentials.get('service', 'moodle_mobile_app')
        return None
    
    def update_credentials(self, host: str, username: str, **updates) -> bool:
        """Update stored credentials"""
        try:
            credentials = self.get_credentials(host, username)
            if not credentials:
                return False
            
            # Update fields
            credentials.update(updates)
            
            # Re-encrypt password if it was updated
            if 'password' in updates:
                credentials['password'] = self._encrypt_data(updates['password'])
            
            # Store updated credentials
            service_name = self._get_credential_service_name(host, username)
            credential_json = json.dumps(credentials)
            keyring.set_password(service_name, "credentials", credential_json)
            
            # Update cache
            self.credentials_cache[f"{host}_{username}"] = credentials
            
            logger.info(f"Credentials updated for {username}@{host}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update credentials: {e}")
            return False
    
    def _validate_credential_inputs(self, host: str, username: str, password: str, service: str) -> bool:
        """Validate credential inputs for security"""
        errors = []
        
        # Validate host
        if not host or not host.strip():
            errors.append("Host cannot be empty")
        elif not (host.startswith('http://') or host.startswith('https://')):
            errors.append("Host must start with http:// or https://")
        elif len(host) > 255:
            errors.append("Host URL too long")
        
        # Validate username
        if not username or not username.strip():
            errors.append("Username cannot be empty")
        elif len(username) > 100:
            errors.append("Username too long")
        elif any(char in username for char in ['<', '>', '"', "'", '&']):
            errors.append("Username contains invalid characters")
        
        # Validate password
        if not password:
            errors.append("Password cannot be empty")
        elif len(password) > 1024:  # Reasonable limit
            errors.append("Password too long")
        
        # Validate service
        if not service or not service.strip():
            errors.append("Service cannot be empty")
        elif len(service) > 50:
            errors.append("Service name too long")
        
        if errors:
            logger.warning(f"Credential validation failed: {'; '.join(errors)}")
            return False
        
        return True
    
    def _get_device_fingerprint(self) -> str:
        """Generate a device fingerprint for security tracking"""
        try:
            import platform
            import uuid
            import hashlib
            
            # Collect device information
            system_info = platform.system() + platform.release()
            machine_id = str(uuid.getnode())
            python_version = platform.python_version()
            
            # Create fingerprint
            fingerprint_data = f"{system_info}_{machine_id}_{python_version}"
            return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
            
        except Exception:
            return "unknown_device"
    
    def _audit_credential_storage(self, cache_key: str, action: str):
        """Audit credential storage operations for security"""
        try:
            audit_data = {
                'action': action,
                'timestamp': datetime.now().isoformat(),
                'cache_key': cache_key,
                'device_fingerprint': self._get_device_fingerprint()
            }
            
            # Store audit log (in production, this could go to a secure audit system)
            audit_key = f"audit_{action}_{cache_key}"
            self.session_data[audit_key] = audit_data
            
            logger.debug(f"Credential audit: {action} for {cache_key}")
            
        except Exception as e:
            logger.error(f"Failed to audit credential storage: {e}")
    
    def delete_credentials(self, host: str, username: str) -> bool:
        """Delete stored credentials"""
        try:
            service_name = self._get_credential_service_name(host, username)
            keyring.delete_password(service_name, "credentials")
            
            # Remove from cache
            cache_key = f"{host}_{username}"
            if cache_key in self.credentials_cache:
                del self.credentials_cache[cache_key]
            
            logger.info(f"Credentials deleted for {username}@{host}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete credentials: {e}")
            return False
    
    def get_all_credentials(self) -> Dict[str, Dict[str, Any]]:
        """Get all stored credentials (without sensitive data) as a dictionary"""
        stored_credentials = {}
        
        try:
            # This is a simplified approach - in practice, you'd need to enumerate keyring entries
            for cache_key, credential_data in self.credentials_cache.items():
                if credential_data.get('remember_me', False):
                    safe_data = {
                        'host': credential_data['host'],
                        'username': credential_data['username'],
                        'service': credential_data['service'],
                        'remember_me': credential_data.get('remember_me', False),
                        'created_at': credential_data.get('created_at'),
                        'last_used': credential_data.get('last_used')
                    }
                    # Use host as key for easy lookup
                    stored_credentials[credential_data['host']] = safe_data
            
        except Exception as e:
            logger.error(f"Failed to get all credentials: {e}")
        
        return stored_credentials
    
    def list_stored_credentials(self) -> List[Dict[str, Any]]:
        """List all stored credentials (without sensitive data)"""
        stored_credentials = []
        
        try:
            # This is a simplified approach - in practice, you'd need to enumerate keyring entries
            for cache_key, credential_data in self.credentials_cache.items():
                if credential_data.get('remember_me', False):
                    safe_data = {
                        'host': credential_data['host'],
                        'username': credential_data['username'],
                        'service': credential_data['service'],
                        'created_at': credential_data.get('created_at'),
                        'last_used': credential_data.get('last_used')
                    }
                    stored_credentials.append(safe_data)
            
        except Exception as e:
            logger.error(f"Failed to list credentials: {e}")
        
        return stored_credentials
    
    def _load_cached_credentials(self):
        """Load credentials from cache file"""
        try:
            cache_file = os.path.join(os.path.expanduser('~'), f'.{self.app_name.lower()}_credentials.cache')
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Only load non-sensitive data
                for key, data in cache_data.items():
                    if data.get('remember_me', False):
                        # Don't load passwords into cache, just metadata
                        self.credentials_cache[key] = {
                            'host': data['host'],
                            'username': data['username'],
                            'service': data.get('service', 'moodle_mobile_app'),
                            'remember_me': True,
                            'created_at': data.get('created_at'),
                            'last_used': data.get('last_used')
                        }
                
                logger.info(f"Loaded {len(self.credentials_cache)} cached credentials")
                
        except Exception as e:
            logger.error(f"Failed to load cached credentials: {e}")
    
    def store_session_data(self, host: str, username: str, session_data: Dict[str, Any]):
        """Store session-related data"""
        try:
            session_key = f"{host}_{username}"
            self.session_data[session_key] = {
                'data': session_data,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=24)  # 24-hour session
            }
            
            logger.info(f"Session data stored for {username}@{host}")
            
        except Exception as e:
            logger.error(f"Failed to store session data: {e}")
    
    def get_session_data(self, host: str, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        try:
            session_key = f"{host}_{username}"
            session_info = self.session_data.get(session_key)
            
            if not session_info:
                return None
            
            # Check if session is expired
            if datetime.now() > session_info['expires_at']:
                del self.session_data[session_key]
                logger.info(f"Session expired for {username}@{host}")
                return None
            
            return session_info['data']
            
        except Exception as e:
            logger.error(f"Failed to retrieve session data: {e}")
            return None
    
    def clear_session_data(self, host: str, username: str):
        """Clear session data"""
        try:
            session_key = f"{host}_{username}"
            if session_key in self.session_data:
                del self.session_data[session_key]
                logger.info(f"Session data cleared for {username}@{host}")
                
        except Exception as e:
            logger.error(f"Failed to clear session data: {e}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            expired_keys = []
            current_time = datetime.now()
            
            for session_key, session_info in self.session_data.items():
                if current_time > session_info['expires_at']:
                    expired_keys.append(session_key)
            
            for key in expired_keys:
                del self.session_data[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
    
    def start_session_monitor(self, check_interval: int = 300):
        """Start automatic session monitoring with timeout handling"""
        import threading
        import time
        
        def monitor_sessions():
            """Background thread to monitor and clean up expired sessions"""
            while True:
                try:
                    # Clean up expired sessions
                    self.cleanup_expired_sessions()
                    
                    # Check for sessions about to expire and log warnings
                    self._check_session_expiry_warnings()
                    
                    # Sleep for the specified interval
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in session monitor: {e}")
                    time.sleep(check_interval)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_sessions, daemon=True)
        monitor_thread.start()
        logger.info(f"Session monitor started with {check_interval}s interval")
    
    def _check_session_expiry_warnings(self):
        """Check for sessions about to expire and log warnings"""
        try:
            current_time = datetime.now()
            warning_threshold = timedelta(hours=1)  # Warn 1 hour before expiry
            
            for session_key, session_info in self.session_data.items():
                if session_key.startswith('session_'):
                    expires_at = datetime.fromisoformat(session_info['expires_at'])
                    time_until_expiry = expires_at - current_time
                    
                    # Log warning if session is about to expire
                    if time_until_expiry <= warning_threshold and time_until_expiry > timedelta(0):
                        username = session_info['username']
                        host = session_info['host']
                        session_id = session_info['session_id'][:8]
                        
                        logger.warning(f"Session {session_id}... for {username}@{host} expires in {time_until_expiry}")
                        
        except Exception as e:
            logger.error(f"Failed to check session expiry warnings: {e}")
    
    def get_session_timeout_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session timeout status"""
        try:
            session_info = self.get_session(session_id)
            if not session_info:
                return {
                    'session_id': session_id,
                    'is_active': False,
                    'is_expired': True,
                    'status': 'not_found',
                    'message': 'Session not found',
                    'time_remaining': None,
                    'expiry_time': None
                }
            
            current_time = datetime.now()
            expires_at = datetime.fromisoformat(session_info['expires_at'])
            time_remaining = expires_at - current_time
            
            # Determine session status
            if time_remaining.total_seconds() <= 0:
                status = 'expired'
                message = 'Session has expired'
                is_expired = True
                is_active = False
            elif time_remaining.total_seconds() <= 3600:  # Less than 1 hour
                status = 'expiring_soon'
                message = 'Session expires soon'
                is_expired = False
                is_active = True
            elif time_remaining.total_seconds() <= 7200:  # Less than 2 hours
                status = 'warning'
                message = 'Session expiry approaching'
                is_expired = False
                is_active = True
            else:
                status = 'active'
                message = 'Session is active'
                is_expired = False
                is_active = True
            
            return {
                'session_id': session_id,
                'is_active': is_active,
                'is_expired': is_expired,
                'status': status,
                'message': message,
                'time_remaining': str(time_remaining),
                'time_remaining_seconds': time_remaining.total_seconds(),
                'expiry_time': expires_at.isoformat(),
                'last_activity': session_info.get('last_activity'),
                'username': session_info.get('username'),
                'host': session_info.get('host')
            }
            
        except Exception as e:
            logger.error(f"Failed to get session timeout status: {e}")
            return {
                'session_id': session_id,
                'is_active': False,
                'is_expired': True,
                'status': 'error',
                'message': f'Error checking session status: {str(e)}',
                'time_remaining': None,
                'expiry_time': None
            }
    
    def auto_extend_session(self, session_id: str, extend_threshold: int = 3600) -> bool:
        """Automatically extend session if it's about to expire"""
        try:
            timeout_status = self.get_session_timeout_status(session_id)
            
            if not timeout_status['is_active']:
                return False
            
            # Check if session needs extension
            time_remaining = timeout_status['time_remaining_seconds']
            if time_remaining and time_remaining <= extend_threshold:
                # Extend session by 24 hours
                success = self.extend_session(session_id, 24)
                if success:
                    logger.info(f"Auto-extended session {session_id[:8]}...")
                return success
            
            return True  # No extension needed
            
        except Exception as e:
            logger.error(f"Failed to auto-extend session: {e}")
            return False
    
    def create_session(self, host: str, username: str, session_data: Dict[str, Any] = None) -> str:
        """Create a new session with enhanced security and timeout handling"""
        try:
            # Validate session inputs
            if not self._validate_session_inputs(host, username):
                return ""
            
            # Check for existing active sessions
            existing_session = self.get_session_by_host_user(host, username)
            if existing_session and existing_session.get('is_active', False):
                logger.warning(f"Active session already exists for {username}@{host}, terminating old session")
                self.delete_session(existing_session['session_id'])
            
            # Generate secure session ID
            session_id = self._generate_session_id(host, username)
            
            # Calculate session timeout (configurable)
            session_timeout = timedelta(hours=24)  # Default 24 hours
            if session_data and 'session_timeout' in session_data:
                try:
                    timeout_hours = int(session_data['session_timeout'])
                    session_timeout = timedelta(hours=timeout_hours)
                except (ValueError, TypeError):
                    logger.warning("Invalid session timeout, using default")
            
            # Create enhanced session info
            current_time = datetime.now()
            session_info = {
                'session_id': session_id,
                'host': host,
                'username': username,
                'created_at': current_time.isoformat(),
                'last_activity': current_time.isoformat(),
                'expires_at': (current_time + session_timeout).isoformat(),
                'is_active': True,
                'security_level': 'high',
                'device_fingerprint': self._get_device_fingerprint(),
                'ip_address': session_data.get('ip_address', 'unknown') if session_data else 'unknown',
                'user_agent': session_data.get('user_agent', 'unknown') if session_data else 'unknown',
                'session_timeout_hours': int(session_timeout.total_seconds() / 3600),
                'data': session_data or {}
            }
            
            # Store session with enhanced key
            session_key = f"session_{session_id}"
            self.session_data[session_key] = session_info
            
            # Also store by host/username for easy lookup
            host_user_key = f"{host}_{username}"
            self.session_data[host_user_key] = session_id
            
            # Create session audit log
            self._audit_session_operation(session_id, 'create', host, username)
            
            logger.info(f"Secure session created for {username}@{host} (ID: {session_id[:8]}..., timeout: {session_timeout})")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return ""
    
    def _validate_session_inputs(self, host: str, username: str) -> bool:
        """Validate session inputs for security"""
        errors = []
        
        # Validate host
        if not host or not host.strip():
            errors.append("Host cannot be empty")
        elif not (host.startswith('http://') or host.startswith('https://')):
            errors.append("Host must start with http:// or https://")
        
        # Validate username
        if not username or not username.strip():
            errors.append("Username cannot be empty")
        elif len(username) > 100:
            errors.append("Username too long")
        
        if errors:
            logger.warning(f"Session validation failed: {'; '.join(errors)}")
            return False
        
        return True
    
    def _audit_session_operation(self, session_id: str, operation: str, host: str, username: str):
        """Audit session operations for security"""
        try:
            audit_data = {
                'operation': operation,
                'session_id': session_id,
                'host': host,
                'username': username,
                'timestamp': datetime.now().isoformat(),
                'device_fingerprint': self._get_device_fingerprint()
            }
            
            # Store audit log
            audit_key = f"session_audit_{operation}_{session_id}"
            self.session_data[audit_key] = audit_data
            
            logger.debug(f"Session audit: {operation} for session {session_id[:8]}...")
            
        except Exception as e:
            logger.error(f"Failed to audit session operation: {e}")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information by ID with enhanced security validation"""
        try:
            session_key = f"session_{session_id}"
            session_info = self.session_data.get(session_key)
            
            if not session_info:
                logger.warning(f"Session not found: {session_id[:8]}...")
                return None
            
            # Check if session is expired
            if self._is_session_expired(session_info):
                logger.info(f"Session {session_id[:8]}... has expired, cleaning up")
                self.delete_session(session_id)
                return None
            
            # Validate session integrity
            if not self._validate_session_integrity(session_info):
                logger.warning(f"Session integrity check failed for {session_id[:8]}...")
                self.delete_session(session_id)
                return None
            
            # Check device fingerprint for security
            current_fingerprint = self._get_device_fingerprint()
            if session_info.get('device_fingerprint') != current_fingerprint:
                logger.warning(f"Device fingerprint mismatch for session {session_id[:8]}...")
                # Optionally terminate session or require re-authentication
                # For now, log the warning but allow continuation
            
            # Update last activity and audit
            session_info['last_activity'] = datetime.now().isoformat()
            self._audit_session_operation(session_id, 'access', session_info['host'], session_info['username'])
            
            return session_info
            
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def _validate_session_integrity(self, session_info: Dict[str, Any]) -> bool:
        """Validate session integrity and required fields"""
        required_fields = ['session_id', 'host', 'username', 'created_at', 'expires_at', 'is_active']
        
        for field in required_fields:
            if field not in session_info:
                logger.warning(f"Session missing required field: {field}")
                return False
        
        # Validate session ID format
        session_id = session_info.get('session_id', '')
        if not session_id or len(session_id) < 16:
            logger.warning("Invalid session ID format")
            return False
        
        # Validate timestamps
        try:
            datetime.fromisoformat(session_info['created_at'])
            datetime.fromisoformat(session_info['expires_at'])
        except (ValueError, TypeError):
            logger.warning("Invalid session timestamps")
            return False
        
        return True
    
    def get_session_by_host_user(self, host: str, username: str) -> Optional[Dict[str, Any]]:
        """Get session by host and username"""
        try:
            host_user_key = f"{host}_{username}"
            session_id = self.session_data.get(host_user_key)
            
            if not session_id:
                return None
            
            return self.get_session(session_id)
            
        except Exception as e:
            logger.error(f"Failed to get session by host/user: {e}")
            return None
    
    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            session_info = self.get_session(session_id)
            if not session_info:
                return False
            
            # Update session data
            session_info['data'].update(session_data)
            session_info['last_activity'] = datetime.now().isoformat()
            
            logger.info(f"Session {session_id[:8]}... updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            session_key = f"session_{session_id}"
            session_info = self.session_data.get(session_key)
            
            if session_info:
                # Remove from host/username mapping
                host_user_key = f"{session_info['host']}_{session_info['username']}"
                if host_user_key in self.session_data:
                    del self.session_data[host_user_key]
                
                # Remove session
                del self.session_data[session_key]
                
                logger.info(f"Session {session_id[:8]}... deleted")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of all active sessions"""
        try:
            active_sessions = []
            
            for key, session_info in self.session_data.items():
                if key.startswith('session_') and not self._is_session_expired(session_info):
                    active_sessions.append(session_info)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return []
    
    def extend_session(self, session_id: str, additional_hours: int = 24) -> bool:
        """Extend session expiry time"""
        try:
            session_info = self.get_session(session_id)
            if not session_info:
                return False
            
            # Extend expiry
            current_expiry = datetime.fromisoformat(session_info['expires_at'])
            new_expiry = current_expiry + timedelta(hours=additional_hours)
            session_info['expires_at'] = new_expiry.isoformat()
            
            logger.info(f"Session {session_id[:8]}... extended by {additional_hours} hours")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extend session: {e}")
            return False
    
    def _generate_session_id(self, host: str, username: str) -> str:
        """Generate a unique session ID"""
        import uuid
        unique_string = f"{host}_{username}_{datetime.now().isoformat()}_{uuid.uuid4()}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _is_session_expired(self, session_info: Dict[str, Any]) -> bool:
        """Check if a session has expired"""
        try:
            expires_at = datetime.fromisoformat(session_info['expires_at'])
            return datetime.now() > expires_at
        except Exception:
            # If we can't parse the expiry time, consider it expired
            return True
    
    def is_token_expired(self, token_expiry: Optional[datetime]) -> bool:
        """Check if token is expired or needs refresh"""
        if not token_expiry:
            return True
        
        return datetime.now() >= (token_expiry - self.token_refresh_threshold)
    
    def generate_device_id(self) -> str:
        """Generate a unique device identifier"""
        try:
            # Use system-specific information to generate a device ID
            import platform
            import uuid
            
            system_info = f"{platform.system()}-{platform.machine()}-{platform.node()}"
            device_hash = hashlib.md5(system_info.encode()).hexdigest()
            
            return f"device_{device_hash}_{uuid.uuid4().hex[:8]}"
            
        except Exception as e:
            logger.error(f"Failed to generate device ID: {e}")
            return f"device_{uuid.uuid4().hex}"
    
    def validate_credentials_format(self, username: str, password: str) -> Tuple[bool, str]:
        """Validate credential format and provide feedback"""
        if not username or not username.strip():
            return False, "Username cannot be empty"
        
        if not password or not password.strip():
            return False, "Password cannot be empty"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        # Check for potentially problematic characters
        problematic_chars = ['"', "'", ';', '\\', '/']
        for char in problematic_chars:
            if char in username or char in password:
                return False, f"Credentials contain invalid character: {char}"
        
        return True, "Credentials format is valid"
    
    def setup_mfa(self, host: str, username: str, mfa_type: str = "totp") -> Dict[str, Any]:
        """Setup multi-factor authentication for a user with enhanced security"""
        try:
            # Validate MFA type
            if mfa_type not in ["totp", "email"]:
                return {
                    'success': False,
                    'error': f'Unsupported MFA type: {mfa_type}'
                }
            
            # Check if MFA is already configured
            current_mfa_status = self.get_mfa_status(host, username)
            if current_mfa_status.get('enabled', False):
                return {
                    'success': False,
                    'error': 'MFA is already enabled for this account'
                }
            
            # Get existing credentials
            credentials = self.get_credentials(host, username)
            if not credentials:
                return {
                    'success': False,
                    'error': 'Credentials not found'
                }
            
            # Generate MFA configuration based on type
            if mfa_type == "totp":
                import pyotp
                
                # Generate secure TOTP secret
                secret = pyotp.random_base32()
                
                # Create provisioning URI for QR code
                provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                    name=username,
                    issuer_name=f"Moodle Manager ({host})"
                )
                
                # Store MFA configuration
                mfa_config = {
                    'type': mfa_type,
                    'secret': secret,
                    'enabled': False,  # Not enabled until verified
                    'setup_at': datetime.now().isoformat(),
                    'backup_codes': self._generate_backup_codes(),
                    'provisioning_uri': provisioning_uri,
                    'algorithm': 'SHA1',
                    'digits': 6,
                    'period': 30,
                    'security_level': 'high'
                }
                
            elif mfa_type == "email":
                # Email-based MFA configuration
                mfa_config = {
                    'type': mfa_type,
                    'enabled': False,
                    'setup_at': datetime.now().isoformat(),
                    'backup_codes': self._generate_backup_codes(),
                    'email_address': credentials.get('email', ''),  # Use stored email if available
                    'security_level': 'medium'
                }
            
            # Add MFA config to credentials
            credentials['mfa'] = mfa_config
            
            # Update credentials
            success = self.update_credentials(host, username, **credentials)
            
            if success:
                # Audit MFA setup
                self._audit_mfa_operation(host, username, 'setup', mfa_type)
                
                logger.info(f"MFA setup initiated for {username}@{host} (type: {mfa_type})")
                
                return {
                    'success': True,
                    'mfa_type': mfa_type,
                    'backup_codes': mfa_config['backup_codes'],
                    'provisioning_uri': mfa_config.get('provisioning_uri'),
                    'message': f'MFA setup initiated. Please verify your {mfa_type.upper()} configuration.'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to store MFA configuration'
                }
            
        except Exception as e:
            logger.error(f"Failed to setup MFA: {e}")
            return {
                'success': False,
                'error': f'MFA setup failed: {str(e)}'
            }
    
    def _audit_mfa_operation(self, host: str, username: str, operation: str, mfa_type: str):
        """Audit MFA operations for security"""
        try:
            audit_data = {
                'operation': operation,
                'mfa_type': mfa_type,
                'host': host,
                'username': username,
                'timestamp': datetime.now().isoformat(),
                'device_fingerprint': self._get_device_fingerprint()
            }
            
            # Store audit log
            audit_key = f"mfa_audit_{operation}_{host}_{username}"
            self.session_data[audit_key] = audit_data
            
            logger.debug(f"MFA audit: {operation} for {username}@{host} ({mfa_type})")
            
        except Exception as e:
            logger.error(f"Failed to audit MFA operation: {e}")
    
    def verify_mfa_setup(self, host: str, username: str, verification_code: str) -> Dict[str, Any]:
        """Verify MFA setup and enable it with enhanced security"""
        try:
            # Validate inputs
            if not verification_code or not verification_code.strip():
                return {
                    'success': False,
                    'error': 'Verification code is required'
                }
            
            # Get credentials
            credentials = self.get_credentials(host, username)
            if not credentials or 'mfa' not in credentials:
                return {
                    'success': False,
                    'error': 'MFA configuration not found'
                }
            
            mfa_config = credentials['mfa']
            
            # Check if MFA is already enabled
            if mfa_config.get('enabled', False):
                return {
                    'success': False,
                    'error': 'MFA is already enabled'
                }
            
            verification_success = False
            verification_method = None
            
            # Verify based on MFA type
            if mfa_config['type'] == 'totp':
                import pyotp
                
                # Validate TOTP code
                totp = pyotp.TOTP(mfa_config['secret'])
                
                # Check if the code is valid (with window for time drift)
                if totp.verify(verification_code, valid_window=1):
                    verification_success = True
                    verification_method = 'totp'
                    logger.info(f"TOTP verification successful for {username}@{host}")
                else:
                    logger.warning(f"Invalid TOTP code for {username}@{host}")
            
            elif mfa_config['type'] == 'email':
                # For email-based MFA, we'll accept any code for now
                # In production, this would involve sending and verifying email codes
                if len(verification_code) >= 6:  # Basic validation
                    verification_success = True
                    verification_method = 'email'
                    logger.info(f"Email verification successful for {username}@{host}")
                else:
                    logger.warning(f"Invalid email verification code for {username}@{host}")
            
            if verification_success:
                # Enable MFA
                mfa_config['enabled'] = True
                mfa_config['verified_at'] = datetime.now().isoformat()
                mfa_config['verification_method'] = verification_method
                
                # Update credentials
                update_success = self.update_credentials(host, username, **credentials)
                
                if update_success:
                    # Audit successful verification
                    self._audit_mfa_operation(host, username, 'verify', mfa_config['type'])
                    
                    return {
                        'success': True,
                        'mfa_type': mfa_config['type'],
                        'verification_method': verification_method,
                        'verified_at': mfa_config['verified_at'],
                        'backup_codes_remaining': len(mfa_config.get('backup_codes', [])),
                        'message': f'MFA successfully enabled using {verification_method.upper()}'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Failed to update MFA configuration'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Invalid verification code'
                }
            
        except Exception as e:
            logger.error(f"Failed to verify MFA setup: {e}")
            return {
                'success': False,
                'error': f'MFA verification failed: {str(e)}'
            }
    
    def add_user_role(self, host: str, username: str, role: str, permissions: List[str] = None) -> bool:
        """Add a role to a user with specific permissions"""
        try:
            credentials = self.get_credentials(host, username)
            if not credentials:
                return False
            
            # Initialize roles if not present
            if 'roles' not in credentials:
                credentials['roles'] = {}
            
            # Add role with permissions
            credentials['roles'][role] = {
                'granted_at': datetime.now().isoformat(),
                'permissions': permissions or [],
                'is_active': True
            }
            
            logger.info(f"Added role '{role}' to user {username}@{host}")
            return self.update_credentials(host, username, **credentials)
            
        except Exception as e:
            logger.error(f"Failed to add user role: {e}")
            return False
    
    def remove_user_role(self, host: str, username: str, role: str) -> bool:
        """Remove a role from a user"""
        try:
            credentials = self.get_credentials(host, username)
            if not credentials or 'roles' not in credentials:
                return False
            
            # Remove role
            if role in credentials['roles']:
                del credentials['roles'][role]
                logger.info(f"Removed role '{role}' from user {username}@{host}")
                return self.update_credentials(host, username, **credentials)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove user role: {e}")
            return False
    
    def get_user_roles(self, host: str, username: str) -> Dict[str, Any]:
        """Get all roles for a user"""
        try:
            credentials = self.get_credentials(host, username)
            if not credentials:
                return {}
            
            return credentials.get('roles', {})
            
        except Exception as e:
            logger.error(f"Failed to get user roles: {e}")
            return {}
    
    def has_permission(self, host: str, username: str, permission: str) -> bool:
        """Check if user has a specific permission"""
        try:
            user_roles = self.get_user_roles(host, username)
            
            # Check each role for the permission
            for role_name, role_data in user_roles.items():
                if role_data.get('is_active', True):
                    if permission in role_data.get('permissions', []):
                        return True
                    
                    # Check for wildcard permissions
                    if '*' in role_data.get('permissions', []):
                        return True
                    
                    # Check for category-based permissions (e.g., 'course:*')
                    if ':' in permission:
                        category = permission.split(':')[0] + ':*'
                        if category in role_data.get('permissions', []):
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check permission: {e}")
            return False
    
    def has_role(self, host: str, username: str, role: str) -> bool:
        """Check if user has a specific role"""
        try:
            user_roles = self.get_user_roles(host, username)
            return role in user_roles and user_roles[role].get('is_active', True)
            
        except Exception as e:
            logger.error(f"Failed to check role: {e}")
            return False
    
    def get_user_permissions(self, host: str, username: str) -> List[str]:
        """Get all permissions for a user"""
        try:
            user_roles = self.get_user_roles(host, username)
            all_permissions = set()
            
            for role_name, role_data in user_roles.items():
                if role_data.get('is_active', True):
                    permissions = role_data.get('permissions', [])
                    all_permissions.update(permissions)
            
            return list(all_permissions)
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return []
    
    def define_role_template(self, role_name: str, permissions: List[str], description: str = "") -> bool:
        """Define a role template that can be assigned to users"""
        try:
            # Store role template in a separate keyring entry
            template_service = f"{self.app_name}_role_templates"
            
            # Get existing templates
            templates_json = keyring.get_password(template_service, "templates")
            templates = json.loads(templates_json) if templates_json else {}
            
            # Add or update template
            templates[role_name] = {
                'permissions': permissions,
                'description': description,
                'created_at': datetime.now().isoformat()
            }
            
            # Save templates
            keyring.set_password(template_service, "templates", json.dumps(templates))
            logger.info(f"Role template '{role_name}' defined with {len(permissions)} permissions")
            return True
            
        except Exception as e:
            logger.error(f"Failed to define role template: {e}")
            return False
    
    def get_role_template(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Get a role template by name"""
        try:
            template_service = f"{self.app_name}_role_templates"
            templates_json = keyring.get_password(template_service, "templates")
            
            if not templates_json:
                return None
            
            templates = json.loads(templates_json)
            return templates.get(role_name)
            
        except Exception as e:
            logger.error(f"Failed to get role template: {e}")
            return None
    
    def assign_role_template(self, host: str, username: str, role_name: str) -> bool:
        """Assign a role template to a user"""
        try:
            template = self.get_role_template(role_name)
            if not template:
                logger.error(f"Role template '{role_name}' not found")
                return False
            
            permissions = template.get('permissions', [])
            return self.add_user_role(host, username, role_name, permissions)
            
        except Exception as e:
            logger.error(f"Failed to assign role template: {e}")
            return False
    
    def get_all_role_templates(self) -> Dict[str, Any]:
        """Get all defined role templates"""
        try:
            template_service = f"{self.app_name}_role_templates"
            templates_json = keyring.get_password(template_service, "templates")
            
            if not templates_json:
                return {}
            
            return json.loads(templates_json)
            
        except Exception as e:
            logger.error(f"Failed to get role templates: {e}")
            return {}
    
    def check_access_control(self, host: str, username: str, required_permissions: List[str]) -> Dict[str, Any]:
        """Comprehensive access control check"""
        try:
            # Get user permissions
            user_permissions = self.get_user_permissions(host, username)
            user_roles = self.get_user_roles(host, username)
            
            # Check each required permission
            missing_permissions = []
            granted_permissions = []
            
            for permission in required_permissions:
                if self.has_permission(host, username, permission):
                    granted_permissions.append(permission)
                else:
                    missing_permissions.append(permission)
            
            # Determine access result
            access_granted = len(missing_permissions) == 0
            
            result = {
                'access_granted': access_granted,
                'granted_permissions': granted_permissions,
                'missing_permissions': missing_permissions,
                'user_permissions': user_permissions,
                'user_roles': list(user_roles.keys()),
                'username': username,
                'host': host
            }
            
            if access_granted:
                logger.info(f"Access granted for {username}@{host} - all permissions satisfied")
            else:
                logger.warning(f"Access denied for {username}@{host} - missing permissions: {missing_permissions}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to check access control: {e}")
            return {
                'access_granted': False,
                'granted_permissions': [],
                'missing_permissions': required_permissions,
                'user_permissions': [],
                'user_roles': [],
                'username': username,
                'host': host,
                'error': str(e)
            }
    
    def validate_mfa_code(self, host: str, username: str, verification_code: str) -> Dict[str, Any]:
        """Validate MFA code during login with enhanced security and rate limiting"""
        try:
            # Validate input
            if not verification_code or not verification_code.strip():
                return {
                    'success': False,
                    'error': 'Verification code is required',
                    'attempts_remaining': 3
                }
            
            # Get credentials
            credentials = self.get_credentials(host, username)
            if not credentials or 'mfa' not in credentials:
                # No MFA configured, allow login
                return {
                    'success': True,
                    'mfa_required': False,
                    'message': 'No MFA configured'
                }
            
            mfa_config = credentials['mfa']
            
            if not mfa_config.get('enabled', False):
                # MFA not enabled, allow login
                return {
                    'success': True,
                    'mfa_required': False,
                    'message': 'MFA not enabled'
                }
            
            # Check rate limiting
            rate_limit_key = f"mfa_attempts_{host}_{username}"
            current_time = datetime.now()
            
            if rate_limit_key in self.session_data:
                attempts_data = self.session_data[rate_limit_key]
                attempts = attempts_data.get('attempts', 0)
                last_attempt = datetime.fromisoformat(attempts_data.get('last_attempt'))
                
                # Check if too many attempts
                if attempts >= 5:
                    # Lock for 15 minutes
                    if (current_time - last_attempt).total_seconds() < 900:
                        return {
                            'success': False,
                            'error': 'Too many failed attempts. Please try again later.',
                            'attempts_remaining': 0,
                            'lockout_time': 900 - int((current_time - last_attempt).total_seconds())
                        }
                    else:
                        # Reset attempts after lockout period
                        attempts = 0
            else:
                attempts = 0
            
            validation_success = False
            validation_method = None
            backup_code_used = False
            
            # Check backup codes first (highest priority)
            backup_codes = mfa_config.get('backup_codes', [])
            if verification_code in backup_codes:
                # Remove used backup code
                backup_codes.remove(verification_code)
                mfa_config['backup_codes'] = backup_codes
                self.update_credentials(host, username, **credentials)
                
                validation_success = True
                validation_method = 'backup_code'
                backup_code_used = True
                
                logger.info(f"MFA backup code used for {username}@{host}")
            
            # Check TOTP
            elif mfa_config['type'] == 'totp':
                import pyotp
                totp = pyotp.TOTP(mfa_config['secret'])
                
                # Validate with time window for clock drift
                if totp.verify(verification_code, valid_window=1):
                    validation_success = True
                    validation_method = 'totp'
                    logger.info(f"MFA TOTP verified for {username}@{host}")
                else:
                    logger.warning(f"Invalid TOTP code for {username}@{host}")
            
            # Check email-based MFA
            elif mfa_config['type'] == 'email':
                # For email-based MFA, accept any 6+ character code for now
                if len(verification_code) >= 6:
                    validation_success = True
                    validation_method = 'email'
                    logger.info(f"MFA email code verified for {username}@{host}")
                else:
                    logger.warning(f"Invalid email verification code for {username}@{host}")
            
            # Update rate limiting
            if validation_success:
                # Reset attempts on success
                if rate_limit_key in self.session_data:
                    del self.session_data[rate_limit_key]
                
                # Audit successful validation
                self._audit_mfa_operation(host, username, 'validate', validation_method)
                
                return {
                    'success': True,
                    'mfa_required': True,
                    'validation_method': validation_method,
                    'backup_code_used': backup_code_used,
                    'backup_codes_remaining': len(mfa_config.get('backup_codes', [])),
                    'message': f'MFA validation successful using {validation_method.replace("_", " ").title()}'
                }
            else:
                # Increment failed attempts
                attempts += 1
                attempts_remaining = max(0, 5 - attempts)
                
                self.session_data[rate_limit_key] = {
                    'attempts': attempts,
                    'last_attempt': current_time.isoformat()
                }
                
                logger.warning(f"MFA validation failed for {username}@{host} (attempt {attempts}/5)")
                
                return {
                    'success': False,
                    'error': 'Invalid verification code',
                    'attempts_remaining': attempts_remaining,
                    'mfa_required': True
                }
            
        except Exception as e:
            logger.error(f"Failed to validate MFA code: {e}")
            return {
                'success': False,
                'error': f'MFA validation failed: {str(e)}',
                'attempts_remaining': 3
            }
    
    def get_mfa_status(self, host: str, username: str) -> Dict[str, Any]:
        """Get detailed MFA status for user"""
        try:
            credentials = self.get_credentials(host, username)
            if not credentials or 'mfa' not in credentials:
                return {
                    'enabled': False,
                    'configured': False,
                    'type': None,
                    'security_level': 'none',
                    'backup_codes_available': 0,
                    'can_setup': True,
                    'recommendations': ['Consider enabling MFA for enhanced security']
                }
            
            mfa_config = credentials['mfa']
            mfa_type = mfa_config.get('type')
            is_enabled = mfa_config.get('enabled', False)
            
            # Calculate security level
            if is_enabled:
                if mfa_type == 'totp':
                    security_level = 'high'
                elif mfa_type == 'email':
                    security_level = 'medium'
                else:
                    security_level = 'low'
            else:
                security_level = 'none'
            
            # Generate recommendations
            recommendations = []
            if not is_enabled:
                recommendations.append('Complete MFA setup to enable enhanced security')
            
            backup_codes_count = len(mfa_config.get('backup_codes', []))
            if backup_codes_count < 3 and is_enabled:
                recommendations.append('Generate more backup codes for account recovery')
            
            # Check if setup is recent but not verified
            setup_at = mfa_config.get('setup_at')
            verified_at = mfa_config.get('verified_at')
            
            if setup_at and not verified_at:
                recommendations.append('Complete MFA verification to activate protection')
            
            status = {
                'enabled': is_enabled,
                'configured': True,
                'type': mfa_type,
                'security_level': security_level,
                'setup_at': setup_at,
                'verified_at': verified_at,
                'backup_codes_count': backup_codes_count,
                'backup_codes_available': backup_codes_count,
                'can_setup': not is_enabled,
                'can_disable': is_enabled,
                'can_regenerate_backup_codes': is_enabled,
                'recommendations': recommendations,
                'last_updated': mfa_config.get('verified_at') or mfa_config.get('setup_at')
            }
            
            # Add type-specific information
            if mfa_type == 'totp':
                status.update({
                    'algorithm': mfa_config.get('algorithm', 'SHA1'),
                    'digits': mfa_config.get('digits', 6),
                    'period': mfa_config.get('period', 30),
                    'provisioning_uri_available': 'provisioning_uri' in mfa_config
                })
            elif mfa_type == 'email':
                status.update({
                    'email_address': mfa_config.get('email_address', ''),
                    'email_configured': bool(mfa_config.get('email_address'))
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get MFA status: {e}")
            return {
                'enabled': False,
                'configured': False,
                'type': None,
                'security_level': 'none',
                'backup_codes_available': 0,
                'can_setup': False,
                'error': str(e),
                'recommendations': ['Unable to determine MFA status']
            }
    
    def disable_mfa(self, host: str, username: str, verification_code: str) -> bool:
        """Disable MFA for a user"""
        try:
            credentials = self.get_credentials(host, username)
            if not credentials or 'mfa' not in credentials:
                return False  # MFA not configured
            
            mfa_config = credentials['mfa']
            
            # If MFA is enabled, require verification code
            if mfa_config.get('enabled', False) and verification_code:
                validation_result = self.validate_mfa_code(host, username, verification_code)
                if not validation_result.get('success', False):
                    return False
            
            # Remove MFA configuration
            del credentials['mfa']
            success = self.update_credentials(host, username, **credentials)
            
            if success:
                # Audit MFA disable
                self._audit_mfa_operation(host, username, 'disable', 'disabled')
                logger.info(f"MFA disabled for {username}@{host}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to disable MFA: {e}")
            return False
    
    def regenerate_backup_codes(self, host: str, username: str, verification_code: str) -> Dict[str, Any]:
        """Regenerate backup codes for MFA with enhanced security"""
        try:
            # Validate input
            if not verification_code or not verification_code.strip():
                return {
                    'success': False,
                    'error': 'Verification code is required',
                    'backup_codes': []
                }
            
            # Get credentials
            credentials = self.get_credentials(host, username)
            if not credentials or 'mfa' not in credentials:
                return {
                    'success': False,
                    'error': 'MFA not configured',
                    'backup_codes': []
                }
            
            mfa_config = credentials['mfa']
            
            # Check if MFA is enabled
            if not mfa_config.get('enabled', False):
                return {
                    'success': False,
                    'error': 'MFA is not enabled',
                    'backup_codes': []
                }
            
            # Validate verification code
            validation_result = self.validate_mfa_code(host, username, verification_code)
            if not validation_result.get('success', False):
                return {
                    'success': False,
                    'error': 'Invalid verification code',
                    'attempts_remaining': validation_result.get('attempts_remaining', 0),
                    'backup_codes': []
                }
            
            # Store old backup codes count for audit
            old_codes_count = len(mfa_config.get('backup_codes', []))
            
            # Generate new backup codes
            new_backup_codes = self._generate_backup_codes()
            mfa_config['backup_codes'] = new_backup_codes
            mfa_config['backup_codes_regenerated_at'] = datetime.now().isoformat()
            
            # Update credentials
            success = self.update_credentials(host, username, **credentials)
            
            if success:
                # Audit backup code regeneration
                self._audit_mfa_operation(host, username, 'regenerate_backup_codes', mfa_config.get('type'))
                
                logger.info(f"Backup codes regenerated for {username}@{host} (old: {old_codes_count}, new: {len(new_backup_codes)})")
                
                return {
                    'success': True,
                    'backup_codes': new_backup_codes,
                    'backup_codes_count': len(new_backup_codes),
                    'previous_codes_count': old_codes_count,
                    'regenerated_at': mfa_config['backup_codes_regenerated_at'],
                    'message': f'Successfully generated {len(new_backup_codes)} new backup codes',
                    'security_note': 'Please store these codes in a secure location. Old codes are now invalid.'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update backup codes',
                    'backup_codes': []
                }
            
        except Exception as e:
            logger.error(f"Failed to regenerate backup codes: {e}")
            return {
                'success': False,
                'error': f'Backup code regeneration failed: {str(e)}',
                'backup_codes': []
            }
    
    def _generate_backup_codes(self) -> List[str]:
        """Generate secure backup codes for MFA"""
        import random
        import string
        import secrets
        
        backup_codes = []
        
        # Generate 10 backup codes
        for i in range(10):
            # Generate more secure 10-character codes with mixed case and numbers
            # Use cryptographically secure random generator
            code_chars = []
            
            # Ensure at least 2 uppercase, 2 lowercase, 2 digits, and 1 special character
            code_chars.extend(secrets.choice(string.ascii_uppercase) for _ in range(2))
            code_chars.extend(secrets.choice(string.ascii_lowercase) for _ in range(2))
            code_chars.extend(secrets.choice(string.digits) for _ in range(2))
            code_chars.extend(secrets.choice('!@#$%&*') for _ in range(1))
            
            # Fill remaining positions with random characters from all sets
            all_chars = string.ascii_letters + string.digits + '!@#$%&*'
            remaining_length = 10 - len(code_chars)
            code_chars.extend(secrets.choice(all_chars) for _ in range(remaining_length))
            
            # Shuffle the characters to avoid predictable patterns
            random.shuffle(code_chars)
            
            # Create the final code
            code = ''.join(code_chars)
            backup_codes.append(code)
        
        # Ensure all codes are unique
        backup_codes = list(set(backup_codes))
        while len(backup_codes) < 10:
            # Generate additional codes if there were duplicates
            code = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%&*') for _ in range(10))
            if code not in backup_codes:
                backup_codes.append(code)
        
        logger.info(f"Generated {len(backup_codes)} secure backup codes")
        return backup_codes
    
    def get_totp_provisioning_uri(self, host: str, username: str) -> Dict[str, Any]:
        """Get TOTP provisioning URI for QR code generation with enhanced security"""
        try:
            # Validate inputs
            if not host or not username:
                return {
                    'success': False,
                    'error': 'Host and username are required',
                    'provisioning_uri': None
                }
            
            # Get credentials
            credentials = self.get_credentials(host, username)
            if not credentials or 'mfa' not in credentials:
                return {
                    'success': False,
                    'error': 'MFA not configured',
                    'provisioning_uri': None
                }
            
            mfa_config = credentials['mfa']
            
            # Check if MFA type is TOTP
            if mfa_config.get('type') != 'totp':
                return {
                    'success': False,
                    'error': f'MFA type is {mfa_config.get("type")}, not TOTP',
                    'provisioning_uri': None
                }
            
            # Check if TOTP secret is available
            if 'secret' not in mfa_config or not mfa_config['secret']:
                return {
                    'success': False,
                    'error': 'TOTP secret not available',
                    'provisioning_uri': None
                }
            
            import pyotp
            
            # Create TOTP object with enhanced parameters
            totp_params = {
                'digits': mfa_config.get('digits', 6),
                'interval': mfa_config.get('period', 30)
            }
            
            # Add algorithm if specified (default is SHA1)
            if mfa_config.get('algorithm') == 'SHA256':
                totp_params['digest'] = hashlib.sha256
            elif mfa_config.get('algorithm') == 'SHA512':
                totp_params['digest'] = hashlib.sha512
            
            totp = pyotp.TOTP(mfa_config['secret'], **totp_params)
            
            # Create secure provisioning URI
            # Format: otpauth://totp/Label?secret=Secret&issuer=Issuer&algorithm=Algorithm&digits=Digits&period=Period
            label = f"{username}@{host}"
            issuer = f"Moodle Manager ({host})"
            
            # Generate provisioning URI with enhanced parameters
            provisioning_uri = totp.provisioning_uri(name=label, issuer_name=issuer)
            
            # Add additional parameters for enhanced security
            if mfa_config.get('algorithm') and mfa_config['algorithm'] != 'SHA1':
                provisioning_uri += f"&algorithm={mfa_config['algorithm']}"
            
            if mfa_config.get('digits') and mfa_config['digits'] != 6:
                provisioning_uri += f"&digits={mfa_config['digits']}"
            
            if mfa_config.get('period') and mfa_config['period'] != 30:
                provisioning_uri += f"&period={mfa_config['period']}"
            
            # Store the provisioning URI in MFA config for future reference
            if 'provisioning_uri' not in mfa_config:
                mfa_config['provisioning_uri'] = provisioning_uri
                self.update_credentials(host, username, **credentials)
            
            logger.info(f"TOTP provisioning URI generated for {username}@{host}")
            
            return {
                'success': True,
                'provisioning_uri': provisioning_uri,
                'mfa_type': 'totp',
                'algorithm': mfa_config.get('algorithm', 'SHA1'),
                'digits': mfa_config.get('digits', 6),
                'period': mfa_config.get('period', 30),
                'label': label,
                'issuer': issuer,
                'security_level': 'high',
                'message': 'TOTP provisioning URI generated successfully',
                'qr_code_instructions': 'Scan this QR code with your authenticator app'
            }
            
        except Exception as e:
            logger.error(f"Failed to get TOTP provisioning URI: {e}")
            return {
                'success': False,
                'error': f'Failed to generate provisioning URI: {str(e)}',
                'provisioning_uri': None
            }
    
    def migrate_credentials_from_file(self, credential_manager_path: str = None) -> Dict[str, Any]:
        """Migrate credentials from old file-based CredentialManager to new keyring-based storage"""
        try:
            if credential_manager_path is None:
                credential_manager_path = os.path.join(os.path.dirname(__file__), '.credentials')
            
            if not os.path.exists(credential_manager_path):
                return {
                    'success': True,
                    'migrated_count': 0,
                    'message': 'No legacy credentials file found'
                }
            
            # Load legacy credentials
            with open(credential_manager_path, 'r') as f:
                legacy_credentials = json.load(f)
            
            migrated_count = 0
            failed_migrations = []
            
            for service_name, cred_data in legacy_credentials.items():
                try:
                    # Parse service name to extract host and username
                    # Legacy format: "lms_Moodle_http://127.0.0.1/moodle/"
                    # We need to extract the actual URL and username
                    
                    # Check if this is the legacy format with URL in the name
                    if 'http://' in service_name or 'https://' in service_name:
                        # Extract the URL part
                        url_start = service_name.find('http')
                        if url_start != -1:
                            host = service_name[url_start:]
                            # Get username from cred_data
                            username = cred_data.get('username', 'unknown')
                        else:
                            # Fallback to original parsing
                            if '_' in service_name:
                                parts = service_name.split('_')
                                if len(parts) >= 2:
                                    host = parts[0]
                                    username = '_'.join(parts[1:])
                                else:
                                    host = service_name
                                    username = cred_data.get('username', 'unknown')
                            else:
                                host = service_name
                                username = cred_data.get('username', 'unknown')
                    else:
                        # Original parsing for other formats
                        if '_' in service_name:
                            parts = service_name.split('_')
                            if len(parts) >= 2:
                                host = parts[0]
                                username = '_'.join(parts[1:])
                            else:
                                host = service_name
                                username = cred_data.get('username', 'unknown')
                        else:
                            host = service_name
                            username = cred_data.get('username', 'unknown')
                    
                    # Ensure host has proper URL format
                    if not host.startswith('http://') and not host.startswith('https://'):
                        host = f'http://{host}'
                    
                    # Decrypt the password using legacy method
                    legacy_password = cred_data.get('password', '')
                    if legacy_password:
                        # Create a temporary CredentialManager to decrypt
                        temp_cred_manager = self._get_legacy_credential_manager()
                        decrypted_password = temp_cred_manager.decrypt_password(legacy_password)
                        
                        if decrypted_password:
                            # Store using new enhanced method
                            success = self.store_credentials(
                                host=host,
                                username=username,
                                password=decrypted_password,
                                service="moodle_mobile_app",
                                remember_me=cred_data.get('remember', True)
                            )
                            
                            if success:
                                migrated_count += 1
                                logger.info(f"Migrated credentials for {username}@{host}")
                            else:
                                failed_migrations.append(f"{username}@{host}")
                        else:
                            failed_migrations.append(f"{username}@{host} (decryption failed)")
                    else:
                        failed_migrations.append(f"{username}@{host} (no password)")
                        
                except Exception as e:
                    failed_migrations.append(f"{service_name} ({str(e)})")
                    logger.error(f"Failed to migrate credentials for {service_name}: {e}")
            
            # Create backup of legacy file
            backup_path = f"{credential_manager_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                import shutil
                shutil.copy2(credential_manager_path, backup_path)
                logger.info(f"Created backup of legacy credentials at {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup of legacy credentials: {e}")
            
            # Remove legacy file if migration was successful
            if migrated_count > 0 and len(failed_migrations) == 0:
                try:
                    os.remove(credential_manager_path)
                    logger.info(f"Removed legacy credentials file: {credential_manager_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove legacy credentials file: {e}")
            
            return {
                'success': True,
                'migrated_count': migrated_count,
                'failed_migrations': failed_migrations,
                'backup_path': backup_path if migrated_count > 0 else None,
                'message': f'Successfully migrated {migrated_count} credentials to secure storage'
            }
            
        except Exception as e:
            logger.error(f"Failed to migrate credentials: {e}")
            return {
                'success': False,
                'error': f'Credential migration failed: {str(e)}',
                'migrated_count': 0
            }
    
    def _get_legacy_credential_manager(self):
        """Get a legacy CredentialManager instance for migration purposes"""
        try:
            # Import here to avoid circular dependencies
            from core.auth.credential_manager import CredentialManager
            return CredentialManager()
        except ImportError:
            logger.error("Legacy CredentialManager not found")
            return None
    
    def get_all_credentials_summary(self) -> Dict[str, Any]:
        """Get a summary of all stored credentials across both storage systems"""
        try:
            summary = {
                'keyring_credentials': [],
                'legacy_file_credentials': [],
                'total_keyring': 0,
                'total_legacy': 0,
                'migration_needed': False,
                'security_recommendations': []
            }
            
            # Get keyring-based credentials
            try:
                for cache_key in self.credentials_cache.keys():
                    if '_' in cache_key:
                        host, username = cache_key.split('_', 1)
                        cred_data = self.credentials_cache[cache_key]
                        
                        summary['keyring_credentials'].append({
                            'host': host,
                            'username': username,
                            'has_mfa': 'mfa' in cred_data,
                            'mfa_enabled': cred_data.get('mfa', {}).get('enabled', False),
                            'security_level': cred_data.get('security_level', 'unknown'),
                            'created_at': cred_data.get('created_at'),
                            'last_used': cred_data.get('last_used')
                        })
                
                summary['total_keyring'] = len(summary['keyring_credentials'])
                
            except Exception as e:
                logger.error(f"Failed to enumerate keyring credentials: {e}")
            
            # Check for legacy file-based credentials
            legacy_file = os.path.join(os.path.dirname(__file__), '.credentials')
            if os.path.exists(legacy_file):
                try:
                    with open(legacy_file, 'r') as f:
                        legacy_creds = json.load(f)
                    
                    for service_name, cred_data in legacy_creds.items():
                        summary['legacy_file_credentials'].append({
                            'service_name': service_name,
                            'username': cred_data.get('username'),
                            'has_password': bool(cred_data.get('password')),
                            'remember': cred_data.get('remember', False)
                        })
                    
                    summary['total_legacy'] = len(summary['legacy_file_credentials'])
                    summary['migration_needed'] = summary['total_legacy'] > 0
                    
                except Exception as e:
                    logger.error(f"Failed to read legacy credentials: {e}")
            
            # Generate security recommendations
            if summary['migration_needed']:
                summary['security_recommendations'].append(
                    'Legacy file-based credentials found. Consider migrating to secure keyring storage.'
                )
            
            if summary['total_keyring'] > 0:
                mfa_enabled_count = sum(1 for cred in summary['keyring_credentials'] if cred['mfa_enabled'])
                if mfa_enabled_count < summary['total_keyring']:
                    summary['security_recommendations'].append(
                        f'Enable MFA for {summary["total_keyring"] - mfa_enabled_count} accounts to enhance security.'
                    )
            
            if summary['total_keyring'] == 0 and summary['total_legacy'] == 0:
                summary['security_recommendations'].append(
                    'No credentials stored. Configure your Moodle connections to get started.'
                )
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get credentials summary: {e}")
            return {
                'keyring_credentials': [],
                'legacy_file_credentials': [],
                'total_keyring': 0,
                'total_legacy': 0,
                'error': str(e)
            }
    
    def consolidate_credential_storage(self) -> Dict[str, Any]:
        """Consolidate all credential storage into the enhanced keyring-based system"""
        try:
            # First, get current status
            summary = self.get_all_credentials_summary()
            
            if not summary['migration_needed']:
                return {
                    'success': True,
                    'message': 'No consolidation needed. All credentials are already using secure storage.',
                    'summary': summary
                }
            
            # Perform migration
            migration_result = self.migrate_credentials_from_file()
            
            if migration_result['success']:
                # Get updated summary after migration
                updated_summary = self.get_all_credentials_summary()
                
                return {
                    'success': True,
                    'message': f'Credential consolidation completed. Migrated {migration_result["migrated_count"]} credentials.',
                    'migration_result': migration_result,
                    'before_summary': summary,
                    'after_summary': updated_summary
                }
            else:
                return {
                    'success': False,
                    'error': migration_result.get('error', 'Unknown migration error'),
                    'summary': summary
                }
            
        except Exception as e:
            logger.error(f"Failed to consolidate credential storage: {e}")
            return {
                'success': False,
                'error': f'Consolidation failed: {str(e)}'
            }
