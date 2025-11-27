"""
User Session Manager for Moodle Manager
Handles user authentication state, sessions, and profile management
"""

import os
import sys


# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from core.data_models import IUser, ILMS
from core.auth.auth_manager import AuthManager
from core.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class UserSession:
    """Represents a user session"""
    
    def __init__(self, user_id: int, username: str, host: str, 
                 session_id: str = None, login_time: datetime = None):
        self.user_id = user_id
        self.username = username
        self.host = host
        self.session_id = session_id or f"session_{user_id}_{int(datetime.now().timestamp())}"
        self.login_time = login_time or datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        
    def is_expired(self, max_age_hours: int = 24) -> bool:
        """Check if session is expired"""
        return datetime.now() - self.login_time > timedelta(hours=max_age_hours)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'host': self.host,
            'session_id': self.session_id,
            'login_time': self.login_time.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'is_active': self.is_active
        }


class UserSessionManager:
    """Manages user sessions and authentication state"""
    
    def __init__(self, app_name: str = "MoodleManager"):
        self.app_name = app_name
        self.auth_manager = AuthManager(app_name)
        self.database_manager = DatabaseManager()
        self.current_session: Optional[UserSession] = None
        self.current_user: Optional[IUser] = None
        self.current_lms: Optional[ILMS] = None
        self.sessions: Dict[str, UserSession] = {}
        
    def login(self, user: IUser, lms: ILMS, host: str, password: str = "", 
              service: str = "moodle_mobile_app", remember_me: bool = False) -> bool:
        """Login user and create session"""
        try:
            # Validate user
            if not user or not user.get_id():
                logger.error("Invalid user provided for login")
                return False
                
            # Create session
            session = UserSession(
                user_id=user.get_id(),
                username=getattr(user, '_username', f"user_{user.get_id()}"),
                host=host
            )
            
            # Store session
            self.sessions[session.session_id] = session
            self.current_session = session
            self.current_user = user
            self.current_lms = lms
            
            # Store credentials if remember me is checked
            if remember_me and password:
                self.auth_manager.store_credentials(host, session.username, password, service, remember_me)
                
            # Create auth manager session
            auth_session_id = self.auth_manager.create_session(host, session.username, {
                'user_id': user.get_id(),
                'session_id': session.session_id,
                'login_time': session.login_time.isoformat(),
                'lms_type': 'moodle'
            })
            
            if auth_session_id:
                session.session_id = auth_session_id
                
            # Log login to database
            self.database_manager.log_connection(
                server_id=self._get_server_id(host),
                username=session.username,
                connection_time=session.login_time,
                success=True
            )
            
            logger.info(f"User logged in: {session.username} at {host}")
            return True
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
            
    def logout(self) -> bool:
        """Logout current user"""
        try:
            if not self.current_session:
                logger.warning("No active session to logout")
                return False
                
            # Clear session data
            session = self.current_session
            session.is_active = False
            
            # Clear auth manager session
            if self.current_lms:
                host = getattr(self.current_lms, '_host', '')
                username = session.username
                self.auth_manager.clear_session_data(host, username)
                
                # Disconnect LMS
                if hasattr(self.current_lms, 'disconnect'):
                    self.current_lms.disconnect()
                    
            # Clear current session
            self.current_session = None
            self.current_user = None
            self.current_lms = None
            
            # Remove from active sessions
            if session.session_id in self.sessions:
                del self.sessions[session.session_id]
                
            logger.info(f"User logged out: {session.username}")
            return True
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
            
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.current_session is not None and self.current_session.is_active
        
    def get_current_user(self) -> Optional[IUser]:
        """Get current logged in user"""
        return self.current_user
        
    def get_current_lms(self) -> Optional[ILMS]:
        """Get current LMS instance"""
        return self.current_lms
        
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get current session information"""
        if not self.current_session:
            return None
            
        return {
            'user_id': self.current_session.user_id,
            'username': self.current_session.username,
            'host': self.current_session.host,
            'login_time': self.current_session.login_time,
            'last_activity': self.current_session.last_activity,
            'session_duration': datetime.now() - self.current_session.login_time
        }
        
    def update_activity(self):
        """Update current session activity"""
        if self.current_session:
            self.current_session.update_activity()
            
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get session history from database"""
        try:
            # This would query the database for login history
            # For now, return current sessions
            history = []
            for session in list(self.sessions.values())[-limit:]:
                history.append(session.to_dict())
            return history
        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []
            
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            expired_sessions = []
            for session_id, session in self.sessions.items():
                if session.is_expired():
                    expired_sessions.append(session_id)
                    
            for session_id in expired_sessions:
                session = self.sessions[session_id]
                session.is_active = False
                del self.sessions[session_id]
                logger.info(f"Cleaned up expired session: {session.username}")
                
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            
    def auto_login(self, host: str, username: str = None) -> bool:
        """Attempt auto-login using stored credentials"""
        try:
            # Get stored credentials
            if username:
                credentials = self.auth_manager.get_credentials(host, username)
            else:
                # Get most recent credentials for this host
                all_creds = self.auth_manager.get_all_credentials()
                credentials = None
                for cred_host, cred_data in all_creds.items():
                    if cred_host == host:
                        credentials = cred_data
                        break
                        
            if not credentials:
                logger.info(f"No stored credentials found for {host}")
                return False
                
            # This would need to be implemented with actual LMS connection
            # For now, just return that credentials were found
            logger.info(f"Found stored credentials for {credentials.get('username', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Auto-login error: {e}")
            return False
            
    def get_stored_users(self, host: str = None) -> List[Dict[str, Any]]:
        """Get list of users with stored credentials"""
        try:
            stored_creds = self.auth_manager.get_all_credentials()
            users = []
            
            for cred_host, cred_data in stored_creds.items():
                if host and cred_host != host:
                    continue
                    
                users.append({
                    'host': cred_host,
                    'username': cred_data.get('username', ''),
                    'service': cred_data.get('service', ''),
                    'remember_me': cred_data.get('remember_me', False),
                    'last_login': cred_data.get('last_login', '')
                })
                
            return users
        except Exception as e:
            logger.error(f"Error getting stored users: {e}")
            return []
            
    def _get_server_id(self, host: str) -> int:
        """Get server ID by host"""
        try:
            moodle_servers = self.database_manager.get_all_moodle_servers()
            for server in moodle_servers:
                if server['host'] == host:
                    return server['id']
            return 0
        except:
            return 0
            
    def get_user_profile_data(self, user: IUser) -> Dict[str, Any]:
        """Get comprehensive user profile data"""
        try:
            if not user:
                return {}
                
            profile_data = {
                'id': user.get_id(),
                'username': getattr(user, '_username', ''),
                'firstname': user.get_first_name(),
                'lastname': user.get_last_name(),
                'fullname': user.get_full_name(),
                'email': user.get_email(),
                'roles': user.get_roles(),
                'course': user.get_course(),
                'last_access': getattr(user, '_last_access', ''),
                'time_created': getattr(user, '_time_created', ''),
                'notes': getattr(user, '_notes', '')
            }
            
            # Add session info if logged in
            if self.current_session and self.current_session.user_id == user.get_id():
                profile_data['session'] = {
                    'login_time': self.current_session.login_time,
                    'last_activity': self.current_session.last_activity,
                    'session_duration': datetime.now() - self.current_session.login_time
                }
                
            return profile_data
        except Exception as e:
            logger.error(f"Error getting user profile data: {e}")
            return {}
            
    def update_user_profile(self, user: IUser, updates: Dict[str, Any]) -> bool:
        """Update user profile data"""
        try:
            if not user:
                return False
                
            # Update user object
            for key, value in updates.items():
                if hasattr(user, f'_{key}'):
                    setattr(user, f'_{key}', value)
                elif hasattr(user, key):
                    setattr(user, key, value)
                    
            # Reset filter content if name-related fields changed
            if any(key in ['firstname', 'lastname', 'email'] for key in updates.keys()):
                user._filter_content = ""
                
            logger.info(f"Updated profile for user {user.get_id()}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
