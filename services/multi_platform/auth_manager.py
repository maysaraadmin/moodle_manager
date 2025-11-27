#!/usr/bin/env python3
"""
Multi-Platform Authentication Manager for Moodle Manager
Handles authentication across multiple Moodle platforms
"""

import os
import sys
import json
import requests
import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from core.data_models_multi import MoodlePlatform, PlatformCredentials, AuthType, PlatformStatus

logger = logging.getLogger(__name__)


class MultiPlatformAuthManager:
    """Manages authentication for multiple Moodle platforms"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def authenticate_platform(self, platform: MoodlePlatform) -> Tuple[bool, str]:
        """Authenticate with a Moodle platform"""
        try:
            if not platform.is_active:
                return False, "Platform is not active"
            
            # Update status to authenticating
            platform.status = PlatformStatus.AUTHENTICATING
            
            # Choose authentication method based on credentials
            auth_type = platform.credentials.auth_type
            
            if auth_type == AuthType.TOKEN:
                return self._authenticate_with_token(platform)
            elif auth_type == AuthType.USERNAME_PASSWORD:
                return self._authenticate_with_username_password(platform)
            elif auth_type == AuthType.API_KEY:
                return self._authenticate_with_api_key(platform)
            elif auth_type == AuthType.OAUTH2:
                return self._authenticate_with_oauth2(platform)
            else:
                return False, f"Unsupported authentication type: {auth_type.value}"
                
        except Exception as e:
            logger.error(f"Authentication error for platform {platform.name}: {e}")
            platform.status = PlatformStatus.ERROR
            return False, f"Authentication failed: {str(e)}"
    
    def _authenticate_with_token(self, platform: MoodlePlatform) -> Tuple[bool, str]:
        """Authenticate using Moodle token"""
        try:
            token = platform.credentials.token
            if not token:
                return False, "No token provided"
            
            # Test token by making a request to webservice/rest/server.php
            ws_url = f"{platform.url.rstrip('/')}/webservice/rest/server.php"
            
            # Test with core_webservice_get_site_info
            params = {
                'wstoken': token,
                'wsfunction': 'core_webservice_get_site_info',
                'moodlewsrestformat': 'json'
            }
            
            response = self.session.get(ws_url, params=params)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'exception' in data:
                        return False, f"Token validation failed: {data.get('message', 'Unknown error')}"
                    
                    # Store session info
                    self.active_sessions[platform.id] = {
                        'token': token,
                        'user_info': data,
                        'authenticated_at': datetime.now(),
                        'platform_url': platform.url
                    }
                    
                    # Update platform info
                    platform.status = PlatformStatus.CONNECTED
                    platform.site_name = data.get('sitename', 'Unknown')
                    platform.platform_version = data.get('version', 'Unknown')
                    platform.admin_email = data.get('admin', {}).get('email', '')
                    
                    return True, "Authentication successful"
                    
                except json.JSONDecodeError:
                    return False, "Invalid response from Moodle server"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Token authentication error: {str(e)}"
    
    def _authenticate_with_username_password(self, platform: MoodlePlatform) -> Tuple[bool, str]:
        """Authenticate using username and password"""
        try:
            username = platform.credentials.username
            password = platform.credentials.password
            
            if not username or not password:
                return False, "Username and password required"
            
            # First, get a token using username/password
            ws_url = f"{platform.url.rstrip('/')}/login/token.php"
            
            params = {
                'username': username,
                'password': password,
                'service': 'moodle_mobile_app'  # Default service
            }
            
            response = self.session.post(ws_url, data=params)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if 'token' in data:
                        token = data['token']
                        
                        # Now validate the token
                        platform.credentials.token = token
                        return self._authenticate_with_token(platform)
                    elif 'error' in data:
                        return False, f"Login failed: {data.get('error', 'Unknown error')}"
                    else:
                        return False, "Invalid response from login service"
                        
                except json.JSONDecodeError:
                    return False, "Invalid response from login service"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Username/password authentication error: {str(e)}"
    
    def _authenticate_with_api_key(self, platform: MoodlePlatform) -> Tuple[bool, str]:
        """Authenticate using API key"""
        try:
            api_key = platform.credentials.api_key
            if not api_key:
                return False, "No API key provided"
            
            # Test API key by making a request
            ws_url = f"{platform.url.rstrip('/')}/webservice/rest/server.php"
            
            params = {
                'wstoken': api_key,
                'wsfunction': 'core_webservice_get_site_info',
                'moodlewsrestformat': 'json'
            }
            
            response = self.session.get(ws_url, params=params)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'exception' in data:
                        return False, f"API key validation failed: {data.get('message', 'Unknown error')}"
                    
                    # Store session info
                    self.active_sessions[platform.id] = {
                        'api_key': api_key,
                        'user_info': data,
                        'authenticated_at': datetime.now(),
                        'platform_url': platform.url
                    }
                    
                    # Update platform info
                    platform.status = PlatformStatus.CONNECTED
                    platform.site_name = data.get('sitename', 'Unknown')
                    platform.platform_version = data.get('version', 'Unknown')
                    
                    return True, "API key authentication successful"
                    
                except json.JSONDecodeError:
                    return False, "Invalid response from Moodle server"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"API key authentication error: {str(e)}"
    
    def _authenticate_with_oauth2(self, platform: MoodlePlatform) -> Tuple[bool, str]:
        """Authenticate using OAuth2"""
        try:
            client_id = platform.credentials.oauth_client_id
            client_secret = platform.credentials.oauth_client_secret
            
            if not client_id or not client_secret:
                return False, "OAuth2 client ID and secret required"
            
            # OAuth2 implementation would go here
            # For now, return not implemented
            return False, "OAuth2 authentication not yet implemented"
            
        except Exception as e:
            return False, f"OAuth2 authentication error: {str(e)}"
    
    def is_authenticated(self, platform_id: str) -> bool:
        """Check if platform is authenticated"""
        return platform_id in self.active_sessions
    
    def get_session_info(self, platform_id: str) -> Optional[Dict[str, Any]]:
        """Get session information for a platform"""
        return self.active_sessions.get(platform_id)
    
    def logout_platform(self, platform_id: str) -> bool:
        """Logout from a platform"""
        try:
            if platform_id in self.active_sessions:
                del self.active_sessions[platform_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Logout error for platform {platform_id}: {e}")
            return False
    
    def logout_all_platforms(self) -> int:
        """Logout from all platforms"""
        count = len(self.active_sessions)
        self.active_sessions.clear()
        return count
    
    def make_api_request(self, platform_id: str, function: str, **kwargs) -> Tuple[bool, Any]:
        """Make an API request to a specific platform"""
        try:
            session_info = self.get_session_info(platform_id)
            if not session_info:
                return False, "Platform not authenticated"
            
            ws_url = f"{session_info['platform_url'].rstrip('/')}/webservice/rest/server.php"
            
            params = {
                'wstoken': session_info.get('token', session_info.get('api_key')),
                'wsfunction': function,
                'moodlewsrestformat': 'json'
            }
            
            # Add additional parameters
            params.update(kwargs)
            
            response = self.session.get(ws_url, params=params)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'exception' in data:
                        return False, f"API error: {data.get('message', 'Unknown error')}"
                    return True, data
                except json.JSONDecodeError:
                    return False, "Invalid JSON response"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            logger.error(f"API request error for platform {platform_id}: {e}")
            return False, f"Request failed: {str(e)}"
    
    def get_platform_users(self, platform_id: str, criteria: Dict[str, Any] = None) -> Tuple[bool, list]:
        """Get users from a platform"""
        params = {
            'criteria': json.dumps(criteria) if criteria else json.dumps([])
        }
        return self.make_api_request(platform_id, 'core_user_get_users', **params)
    
    def get_platform_courses(self, platform_id: str) -> Tuple[bool, list]:
        """Get courses from a platform"""
        return self.make_api_request(platform_id, 'core_course_get_courses')
    
    def get_platform_categories(self, platform_id: str) -> Tuple[bool, list]:
        """Get categories from a platform"""
        return self.make_api_request(platform_id, 'core_course_get_categories')
    
    def create_platform_user(self, platform_id: str, user_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a user on a platform"""
        params = {
            'users': json.dumps([user_data])
        }
        return self.make_api_request(platform_id, 'core_user_create_users', **params)
    
    def create_platform_course(self, platform_id: str, course_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a course on a platform"""
        params = {
            'courses': json.dumps([course_data])
        }
        return self.make_api_request(platform_id, 'core_course_create_courses', **params)
    
    def enrol_user_in_course(self, platform_id: str, user_id: int, course_id: int, 
                           role_id: int = 5) -> Tuple[bool, Any]:
        """Enrol a user in a course"""
        enrolments = [{
            'roleid': role_id,
            'userid': user_id,
            'courseid': course_id
        }]
        params = {
            'enrolments': json.dumps(enrolments)
        }
        return self.make_api_request(platform_id, 'enrol_manual_enrol_users', **params)
    
    def get_user_profile(self, platform_id: str, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        """Get user profile from a platform"""
        return self.make_api_request(platform_id, 'core_user_get_users_by_field', 
                                  field='id', values=[user_id])
    
    def get_course_content(self, platform_id: str, course_id: int) -> Tuple[bool, list]:
        """Get course content from a platform"""
        return self.make_api_request(platform_id, 'core_course_get_contents', courseid=course_id)
    
    def get_course_users(self, platform_id: str, course_id: int) -> Tuple[bool, list]:
        """Get users enrolled in a course"""
        return self.make_api_request(platform_id, 'core_enrol_get_enrolled_users', courseid=course_id)
    
    def get_site_info(self, platform_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Get site information from a platform"""
        return self.make_api_request(platform_id, 'core_webservice_get_site_info')
    
    def validate_platform_connection(self, platform: MoodlePlatform) -> Tuple[bool, str]:
        """Validate connection to a platform without full authentication"""
        try:
            # Try to access the Moodle front page
            response = self.session.get(platform.url, timeout=10)
            
            if response.status_code == 200:
                # Check if it looks like a Moodle site
                if 'moodle' in response.text.lower() or 'Moodle' in response.text:
                    return True, "Connection successful"
                else:
                    return False, "URL does not appear to be a Moodle site"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def get_authentication_methods(self, platform: MoodlePlatform) -> list:
        """Get available authentication methods for a platform"""
        try:
            # Try to get available web services
            ws_url = f"{platform.url.rstrip('/')}/webservice/rest/server.php"
            
            params = {
                'wstoken': 'test',  # Invalid token to trigger error that shows available services
                'wsfunction': 'core_webservice_get_site_info',
                'moodlewsrestformat': 'json'
            }
            
            response = self.session.get(ws_url, params=params)
            
            # Parse response to determine available auth methods
            available_methods = []
            
            # For now, return all supported methods
            available_methods = [
                AuthType.TOKEN,
                AuthType.USERNAME_PASSWORD,
                AuthType.API_KEY
                # OAuth2 would require additional setup
            ]
            
            return available_methods
            
        except Exception as e:
            logger.error(f"Error getting authentication methods: {e}")
            return [AuthType.TOKEN, AuthType.USERNAME_PASSWORD]  # Default methods
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for platform_id, session_info in self.active_sessions.items():
            authenticated_at = session_info.get('authenticated_at')
            if authenticated_at:
                # Sessions expire after 24 hours by default
                if current_time - authenticated_at > timedelta(hours=24):
                    expired_sessions.append(platform_id)
        
        for platform_id in expired_sessions:
            del self.active_sessions[platform_id]
        
        return len(expired_sessions)
