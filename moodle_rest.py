"""
Moodle REST API Client
Comprehensive Python implementation of the Moodle REST API integration
"""

import requests
import json
import ssl
import certifi
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urljoin
import keyring
from datetime import datetime, timedelta
import logging
from auth_manager import AuthManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoodleRestClient:
    """Comprehensive Moodle REST API client with all required features"""
    
    # Core Web Service Functions
    CORE_WEBSERVICE_GET_SITE_INFO = "core_webservice_get_site_info"
    
    # User Management Functions
    CORE_USER_GET_USERS = "core_user_get_users"
    CORE_USER_GET_USERS_BY_FIELD = "core_user_get_users_by_field"
    CORE_USER_CREATE_USERS = "core_user_create_users"
    CORE_USER_UPDATE_USERS = "core_user_update_users"
    CORE_USER_DELETE_USERS = "core_user_delete_users"
    
    # Course Management Functions
    CORE_COURSE_GET_COURSES = "core_course_get_courses"
    CORE_COURSE_CREATE_COURSES = "core_course_create_courses"
    CORE_COURSE_UPDATE_COURSES = "core_course_update_courses"
    CORE_COURSE_DELETE_COURSES = "core_course_delete_courses"
    CORE_COURSE_GET_CONTENTS = "core_course_get_contents"
    CORE_COURSE_DUPLICATE_COURSE = "core_course_duplicate_course"
    CORE_COURSE_GET_CATEGORIES = "core_course_get_categories"
    CORE_COURSE_CREATE_CATEGORIES = "core_course_create_categories"
    CORE_COURSE_UPDATE_CATEGORIES = "core_course_update_categories"
    CORE_COURSE_DELETE_CATEGORIES = "core_course_delete_categories"
    
    # Backup & Restore Functions
    CORE_BACKUP_SUBMIT_BACKUP = "core_backup_submit_backup"
    CORE_BACKUP_GET_BACKUP = "core_backup_get_backup"
    CORE_RESTORE_SUBMIT_RESTORE = "core_restore_submit_restore"
    
    # Enrollment Functions
    CORE_ENROL_GET_ENROLLED_USERS = "core_enrol_get_enrolled_users"
    CORE_ENROL_GET_USERS_COURSES = "core_enrol_get_users_courses"
    ENROL_MANUAL_ENROL_USERS = "enrol_manual_enrol_users"
    ENROL_MANUAL_UNENROL_USERS = "enrol_manual_unenrol_users"
    
    # Group Functions
    CORE_GROUP_GET_COURSE_GROUPS = "core_group_get_course_groups"
    CORE_GROUP_CREATE_GROUPS = "core_group_create_groups"
    CORE_GROUP_DELETE_GROUPS = "core_group_delete_groups"
    CORE_GROUP_GET_GROUP_MEMBERS = "core_group_get_group_members"
    CORE_GROUP_ADD_GROUP_MEMBERS = "core_group_add_group_members"
    CORE_GROUP_DELETE_GROUP_MEMBERS = "core_group_delete_group_members"
    
    # Gradebook Functions
    CORE_GRADE_GET_GRADE_ITEMS = "core_grade_get_grade_items"
    CORE_GRADE_GET_GRADES = "core_grade_get_grades"
    CORE_GRADE_UPDATE_GRADES = "core_grades_update_grades"
    
    # Role Functions
    CORE_ROLE_ASSIGN_ROLES = "core_role_assign_roles"
    CORE_ROLE_UNASSIGN_ROLES = "core_role_unassign_roles"
    CORE_ROLE_GET_ROLES = "core_role_get_roles"
    
    # Activity Functions
    MOD_ASSIGN_GET_SUBMISSIONS = "mod_assign_get_submissions"
    MOD_ASSIGN_GET_SUBMISSION_STATUS = "mod_assign_get_submission_status"
    MOD_QUIZ_GET_USER_ATTEMPTS = "mod_quiz_get_user_attempts"
    
    # Message Functions
    CORE_MESSAGE_SEND_INSTANT_MESSAGE = "core_message_send_instant_message"
    CORE_MESSAGE_GET_MESSAGES = "core_message_get_messages"
    
    # File Functions
    CORE_FILES_UPLOAD = "core_files_upload"
    CORE_FILES_GET_FILES = "core_files_get_files"
    
    # Calendar Functions
    CORE_CALENDAR_GET_CALENDAR_EVENTS = "core_calendar_get_calendar_events"
    CORE_CALENDAR_CREATE_CALENDAR_EVENTS = "core_calendar_create_calendar_events"
    CORE_CALENDAR_DELETE_CALENDAR_EVENTS = "core_calendar_delete_calendar_events"
    
    # Cohort Functions
    CORE_COHORT_CREATE_COHORTS = "core_cohort_create_cohorts"
    CORE_COHORT_DELETE_COHORTS = "core_cohort_delete_cohorts"
    CORE_COHORT_ADD_COHORT_MEMBERS = "core_cohort_add_cohort_members"
    
    # Backup Functions
    CORE_BACKUP_SUBMIT_BACKUP = "core_backup_submit_backup"
    CORE_BACKUP_GET_BACKUP = "core_backup_get_backup"
    CORE_BACKUP_GET_ASYNC_BACKUP_LINKS_BACKUP = "core_backup_get_async_backup_links_backup"
    CORE_BACKUP_SUBMIT_COPY_FORM = "core_backup_submit_copy_form"
    CORE_RESTORE_SUBMIT_RESTORE = "core_restore_submit_restore"
    
    # Course Content Functions
    CORE_COURSE_GET_COURSE_CONTENT_ITEMS = "core_course_get_course_content_items"
    
    # User Profile Functions
    CORE_USER_GET_COURSE_USER_PROFILES = "core_user_get_course_user_profiles"
    CORE_USER_GET_USER_PREFERENCES = "core_user_get_user_preferences"
    
    # Grade Report Functions
    GRADEREPORT_USER_GET_GRADE_ITEMS = "gradereport_user_get_grade_items"
    
    def __init__(self, host: str, username: str = "", password: str = "", service: str = "moodle_mobile_app"):
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.service = service
        self.token = None
        self.token_expiry = None
        self.verify_ssl = True
        self.debug_mode = False
        self.response_format = 'json'  # Can be 'json' or 'xml'
        self.site_info = None
        self.user_roles = []
        self.token_refresh_threshold = timedelta(hours=1)  # Refresh token 1 hour before expiry
        
        # Initialize authentication manager
        self.auth_manager = AuthManager("MoodleManager")
        
        # Initialize session with proper headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MoodleManager/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        # SSL certificate handling
        self._setup_ssl_verification()
        
        # Try to load token from keyring if available
        if username:
            self._load_token_from_storage()
    
    def _setup_ssl_verification(self):
        """Setup SSL verification with proper certificate handling"""
        if self.verify_ssl:
            try:
                # Use certifi's certificate bundle
                self.session.verify = certifi.where()
                logger.info("SSL verification enabled using certifi bundle")
            except Exception as e:
                logger.warning(f"Failed to load certifi bundle: {e}")
                # Fall back to system certificates
                self.session.verify = True
                logger.info("SSL verification enabled using system certificates")
        else:
            # Development mode - disable SSL verification
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logger.warning("SSL verification disabled (development mode)")
    
    def set_ssl_verification(self, verify: bool):
        """Enable or disable SSL verification"""
        self.verify_ssl = verify
        self._setup_ssl_verification()
        logger.info(f"SSL verification {'enabled' if verify else 'disabled'}")
    
    def _load_token_from_storage(self):
        """Load token from secure storage using keyring"""
        try:
            service_name = f"moodle_manager_{self.host}"
            stored_token = keyring.get_password(service_name, self.username)
            
            if stored_token:
                self.token = stored_token
                logger.info(f"Token loaded from secure storage for user {self.username}")
                
                # Check if token needs refresh
                if self._is_token_expired():
                    logger.warning("Token expired, attempting refresh...")
                    self.refresh_token()
            else:
                logger.info("No stored token found")
                
        except Exception as e:
            logger.error(f"Failed to load token from storage: {e}")
    
    def _save_token_to_storage(self):
        """Save token to secure storage using keyring"""
        if not self.token or not self.username:
            return
            
        try:
            service_name = f"moodle_manager_{self.host}"
            keyring.set_password(service_name, self.username, self.token)
            logger.info(f"Token saved to secure storage for user {self.username}")
        except Exception as e:
            logger.error(f"Failed to save token to storage: {e}")
    
    def _clear_token_from_storage(self):
        """Clear token from secure storage"""
        if not self.username:
            return
            
        try:
            service_name = f"moodle_manager_{self.host}"
            keyring.delete_password(service_name, self.username)
            logger.info(f"Token cleared from secure storage for user {self.username}")
        except Exception as e:
            logger.error(f"Failed to clear token from storage: {e}")
    
    def _get_credentials_from_keyring(self) -> Optional[Dict[str, str]]:
        """Get credentials from keyring storage as fallback"""
        try:
            # Try to get password from keyring
            service_name = f"moodle_manager_{self.host}"
            password = keyring.get_password(service_name, self.username)
            
            if password:
                # Try to get service from keyring as well
                service_key = f"{service_name}_service"
                service = keyring.get_password(service_key, self.username) or self.service
                
                return {
                    'username': self.username,
                    'password': password,
                    'service': service
                }
            else:
                logger.info("No credentials found in keyring")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get credentials from keyring: {e}")
            return None
    
    def _is_token_expired(self) -> bool:
        """Check if token is expired or needs refresh"""
        if not self.token_expiry:
            return True
            
        now = datetime.now()
        return now >= (self.token_expiry - self.token_refresh_threshold)
    
    def _update_token_expiry(self, expiry_time: int = None):
        """Update token expiry time"""
        if expiry_time:
            # Convert timestamp to datetime
            self.token_expiry = datetime.fromtimestamp(expiry_time)
        else:
            # Default expiry: 24 hours from now
            self.token_expiry = datetime.now() + timedelta(hours=24)
        
        logger.info(f"Token expiry set to: {self.token_expiry}")
    
    def refresh_token(self, max_retries: int = 3, retry_delay: float = 1.0) -> bool:
        """Refresh the authentication token using stored credentials with retry logic"""
        import time
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Token refresh attempt {attempt + 1}/{max_retries}")
                
                # Try to get credentials from AuthManager first
                credentials = self.auth_manager.get_credentials(self.host, self.username)
                
                if credentials:
                    # Use stored credentials
                    username = credentials['username']
                    password = credentials['password']
                    service = credentials.get('service', self.service)
                    logger.info(f"Using stored credentials for {username}@{self.host}")
                else:
                    # Try to get credentials from keyring as fallback
                    credentials = self._get_credentials_from_keyring()
                    if credentials:
                        username = credentials['username']
                        password = credentials['password']
                        service = credentials.get('service', self.service)
                        logger.info(f"Using keyring credentials for {username}@{self.host}")
                    else:
                        # Fall back to instance credentials
                        if not self.username or not self.password:
                            logger.error("Cannot refresh token: no credentials available")
                            return False
                        username = self.username
                        password = self.password
                        service = self.service
                        logger.info(f"Using instance credentials for {username}@{self.host}")
                
                # Validate credentials before attempting refresh
                is_valid, validation_msg = self.auth_manager.validate_credentials_format(username, password)
                if not is_valid:
                    logger.error(f"Invalid credentials format: {validation_msg}")
                    return False
                
                # Get new token
                new_token = self._get_token_with_credentials(username, password, service)
                if new_token:
                    # Validate the new token before saving
                    if self._is_token_valid(new_token):
                        self.token = new_token
                        self._update_token_expiry()
                        self._save_token_to_storage()
                        logger.info("Token refreshed successfully")
                        return True
                    else:
                        logger.warning("New token failed validation, retrying...")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                else:
                    logger.error(f"Failed to refresh token on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                        
            except Exception as e:
                logger.error(f"Error refreshing token (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
        
        logger.error(f"Token refresh failed after {max_retries} attempts")
        return False
    
    def auto_refresh_token(self, force_refresh: bool = False) -> bool:
        """Automatically refresh token if it's about to expire or if forced"""
        try:
            if not self.token:
                logger.info("No token available for auto-refresh")
                return False
            
            token_status = self.get_token_status()
            
            # Check if refresh is needed
            needs_refresh = force_refresh or token_status['needs_refresh'] or token_status['status'] in ['expiring_soon', 'expired']
            
            if needs_refresh:
                logger.info(f"Auto-refreshing token (status: {token_status['status']})")
                return self.refresh_token()
            else:
                logger.info(f"Token refresh not needed (status: {token_status['status']})")
                return True
                
        except Exception as e:
            logger.error(f"Error in auto-refresh token: {e}")
            return False
    
    def get_token_status(self) -> Dict[str, Any]:
        """Get current token status information with enhanced details"""
        if not self.token:
            return {
                'has_token': False,
                'is_expired': True,
                'expiry_time': None,
                'time_remaining': None,
                'needs_refresh': True,
                'status': 'no_token',
                'message': 'No authentication token available',
                'suggestions': [
                    'Please login to obtain a new token',
                    'Check your network connection',
                    'Verify your Moodle server URL'
                ]
            }
        
        is_expired = self._is_token_expired()
        time_remaining = None
        status = 'valid'
        message = 'Token is valid'
        suggestions = []
        
        if self.token_expiry:
            time_remaining = self.token_expiry - datetime.now()
            
            if time_remaining.total_seconds() < 0:
                status = 'expired'
                message = 'Token has expired'
                suggestions = [
                    'Token refresh required',
                    'Please login again to obtain a new token',
                    'Check your credentials'
                ]
            elif time_remaining.total_seconds() < 3600:  # Less than 1 hour
                status = 'expiring_soon'
                message = 'Token will expire soon'
                suggestions = [
                    'Token will expire in less than 1 hour',
                    'Consider refreshing your session',
                    'Save your work before token expires'
                ]
            elif time_remaining.total_seconds() < 7200:  # Less than 2 hours
                status = 'warning'
                message = 'Token expiry approaching'
                suggestions = [
                    'Token will expire in less than 2 hours',
                    'Plan to refresh your session soon'
                ]
        
        return {
            'has_token': True,
            'is_expired': is_expired,
            'expiry_time': self.token_expiry.isoformat() if self.token_expiry else None,
            'time_remaining': str(time_remaining) if time_remaining else None,
            'time_remaining_seconds': time_remaining.total_seconds() if time_remaining else None,
            'needs_refresh': is_expired,
            'status': status,
            'message': message,
            'suggestions': suggestions,
            'token_preview': f'{self.token[:10]}...' if len(self.token) > 10 else self.token,
            'host': self.host,
            'username': self.username,
            'service': self.service
        }
    
    def connect(self) -> bool:
        """Connect to Moodle and get authentication token"""
        try:
            # Check if we already have a valid token
            if self.token and not self._is_token_expired():
                logger.info("Using existing valid token")
                return self._validate_token()
            
            # Get new token from Moodle
            new_token = self._get_token()
            if new_token:
                self.token = new_token
                self._update_token_expiry()
                self._save_token_to_storage()
                logger.info("Successfully connected to Moodle")
                return self._validate_token()
            else:
                logger.error("Failed to get token from Moodle")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def _get_token(self) -> Optional[str]:
        """Get authentication token from Moodle using instance credentials"""
        return self._get_token_with_credentials(self.username, self.password, self.service)
    
    def _get_token_with_credentials(self, username: str, password: str, service: str) -> Optional[str]:
        """Get authentication token from Moodle using provided credentials"""
        try:
            # Validate credentials format first
            is_valid, validation_msg = self.auth_manager.validate_credentials_format(username, password)
            if not is_valid:
                logger.error(f"Invalid credentials format: {validation_msg}")
                return None
            
            # Moodle token endpoint
            token_url = f"{self.host}/login/token.php"
            
            params = {
                'username': username,
                'password': password,
                'service': service
            }
            
            if self.debug_mode:
                logger.debug(f"Requesting token from: {token_url}")
                logger.debug(f"Username: {username}, Service: {service}")
            
            response = self.session.post(token_url, data=params)
            
            # Check for HTTP errors
            if response.status_code == 400:
                logger.error("Bad request - invalid parameters")
                return None
            elif response.status_code == 401:
                logger.error("Unauthorized - invalid credentials")
                return None
            elif response.status_code == 403:
                logger.error("Forbidden - access denied")
                return None
            
            response.raise_for_status()
            
            data = response.json()
            
            if 'token' in data:
                logger.info(f"Token obtained successfully for {username}@{self.host}")
                return data['token']
            else:
                error_msg = data.get('error', 'Unknown error')
                error_code = data.get('errorcode', 'unknown')
                logger.error(f"Token request failed [{error_code}]: {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Token request error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Token response JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting token: {e}")
            return None
    
    def _is_token_valid(self, token: str) -> bool:
        """Check if token is valid by making a test API call"""
        try:
            # Test with site info call
            old_token = self.token
            self.token = token
            
            result = self.get_site_info()
            
            # Restore original token
            self.token = old_token
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return False
    
    def _validate_token(self) -> bool:
        """Validate current token by making a test API call"""
        if not self.token:
            return False
            
        try:
            result = self.get_site_info()
            if result:
                logger.info("Token validated successfully")
                return True
            else:
                logger.error("Token validation failed")
                return False
                
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Moodle and clear token"""
        # Clear token from storage
        self._clear_token_from_storage()
        
        # Clear session data
        if self.username:
            self.auth_manager.clear_session_data(self.host, self.username)
        
        # Clear local token data
        self.token = None
        self.token_expiry = None
        self.site_info = None
        self.user_roles = []
        
        logger.info("Disconnected from Moodle")
    
    def store_credentials(self, remember_me: bool = False) -> bool:
        """Store current credentials securely"""
        if not self.username or not self.password:
            logger.error("No credentials to store")
            return False
        
        return self.auth_manager.store_credentials(
            self.host, self.username, self.password, self.service, remember_me
        )
    
    def update_credentials(self, username: str = None, password: str = None, service: str = None) -> bool:
        """Update stored credentials"""
        updates = {}
        if username is not None:
            updates['username'] = username
        if password is not None:
            updates['password'] = password
        if service is not None:
            updates['service'] = service
        
        if not updates:
            logger.warning("No updates provided")
            return False
        
        return self.auth_manager.update_credentials(self.host, self.username, **updates)
    
    def delete_stored_credentials(self) -> bool:
        """Delete stored credentials"""
        if not self.username:
            logger.error("No username to delete credentials for")
            return False
        
        return self.auth_manager.delete_credentials(self.host, self.username)
    
    def has_stored_credentials(self) -> bool:
        """Check if credentials are stored for current user"""
        if not self.username:
            return False
        
        credentials = self.auth_manager.get_credentials(self.host, self.username)
        return credentials is not None
    
    def get_credential_status(self) -> Dict[str, Any]:
        """Get credential storage status"""
        status = {
            'has_credentials': False,
            'remember_me': False,
            'username': self.username,
            'host': self.host,
            'last_used': None,
            'created_at': None
        }
        
        if self.username:
            credentials = self.auth_manager.get_credentials(self.host, self.username)
            if credentials:
                status.update({
                    'has_credentials': True,
                    'remember_me': credentials.get('remember_me', False),
                    'last_used': credentials.get('last_used'),
                    'created_at': credentials.get('created_at')
                })
        
        return status
    
    def is_connected(self) -> bool:
        """Check if connected to Moodle with valid token"""
        return bool(self.token and not self._is_token_expired())
    
    def _make_request(self, function: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make a REST API request to Moodle with comprehensive error handling"""
        if not self.is_connected():
            logger.error("Not connected to Moodle")
            return None
            
        try:
            # Moodle web service endpoint
            ws_url = f"{self.host}/webservice/rest/server.php"
            
            request_params = {
                'wstoken': self.token,
                'wsfunction': function,
                'moodlewsrestformat': self.response_format
            }
            
            if params:
                request_params.update(params)
            
            if self.debug_mode:
                logger.debug(f"Making request to: {ws_url}")
                logger.debug(f"Parameters: {request_params}")
            
            response = self.session.post(ws_url, data=request_params, verify=self.verify_ssl)
            
            # Check for HTTP errors
            if response.status_code == 401:
                logger.error("Authentication failed - token may be expired")
                self.token = ""  # Clear expired token
                return None
            elif response.status_code == 403:
                logger.error("Access denied - insufficient permissions")
                return None
            elif response.status_code >= 500:
                logger.error(f"Server error: {response.status_code}")
                return None
            
            response.raise_for_status()
            
            # Parse response based on format
            if self.response_format == 'json':
                data = response.json()
            else:
                # XML format - would need xmltodict here
                import xmltodict
                data = xmltodict.parse(response.text)
            
            if self.debug_mode:
                logger.debug(f"Response: {data}")
            
            # Check for Moodle errors
            if isinstance(data, dict):
                if 'exception' in data:
                    error_msg = data.get('message', 'Unknown Moodle error')
                    error_code = data.get('errorcode', 'unknown')
                    logger.error(f"Moodle error [{error_code}]: {error_msg}")
                    return None
                elif 'error' in data:
                    logger.error(f"Moodle error: {data['error']}")
                    return None
                
            return data
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL error: {e}")
            if self.verify_ssl:
                logger.info("Try disabling SSL verification for development environments")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    # === Core Site Information ===
    def get_site_info(self) -> Optional[Dict[str, Any]]:
        """Get site information including user details and capabilities"""
        data = self._make_request(self.CORE_WEBSERVICE_GET_SITE_INFO)
        if data:
            self.site_info = data
            # Extract user roles if available
            if 'userprivileges' in data:
                self.user_roles = data['userprivileges']
        return data
    
    # === Category Management ===
    def get_categories(self) -> Optional[List[Dict[str, Any]]]:
        """Get all categories"""
        data = self._make_request(self.CORE_COURSE_GET_CATEGORIES)
        return data if data is not None else None
    
    def create_category(self, name: str, parent: int = 0, description: str = "", 
                       idnumber: str = "", theme: str = "") -> Optional[Dict[str, Any]]:
        """Create a new category"""
        params = {
            'categories[0][name]': name,
            'categories[0][parent]': parent,
            'categories[0][description]': description,
            'categories[0][idnumber]': idnumber,
            'categories[0][theme]': theme
        }
        data = self._make_request(self.CORE_COURSE_CREATE_CATEGORIES, params)
        return data[0] if data and len(data) > 0 else None
    
    def update_category(self, category_id: int, name: str = None, description: str = None,
                       parent: int = None) -> bool:
        """Update an existing category"""
        params = {'categories[0][id]': category_id}
        if name is not None:
            params['categories[0][name]'] = name
        if description is not None:
            params['categories[0][description]'] = description
        if parent is not None:
            params['categories[0][parent]'] = parent
        
        data = self._make_request(self.CORE_COURSE_UPDATE_CATEGORIES, params)
        return data is not None
    
    def delete_category(self, category_id: int, new_parent: int = 0) -> bool:
        """Delete a category"""
        params = {
            'categories[0][id]': category_id,
            'categories[0][newparent]': new_parent
        }
        data = self._make_request(self.CORE_COURSE_DELETE_CATEGORIES, params)
        return data is not None
    
    # === Course Management ===
    def get_courses(self) -> Optional[List[Dict[str, Any]]]:
        """Get all courses"""
        data = self._make_request(self.CORE_COURSE_GET_COURSES)
        return data if data is not None else None
    
    def create_course(self, fullname: str, shortname: str, category_id: int,
                     summary: str = "", format: str = "topics", 
                     visible: bool = True, start_date: int = None,
                     end_date: int = None) -> Optional[Dict[str, Any]]:
        """Create a new course"""
        params = {
            'courses[0][fullname]': fullname,
            'courses[0][shortname]': shortname,
            'courses[0][categoryid]': category_id,
            'courses[0][summary]': summary,
            'courses[0][format]': format,
            'courses[0][visible]': 1 if visible else 0
        }
        
        if start_date is not None:
            params['courses[0][startdate]'] = start_date
        if end_date is not None:
            params['courses[0][enddate]'] = end_date
        
        data = self._make_request(self.CORE_COURSE_CREATE_COURSES, params)
        return data[0] if data and len(data) > 0 else None
    
    def update_course(self, course_id: int, fullname: str = None, shortname: str = None,
                     summary: str = None, visible: bool = None) -> bool:
        """Update an existing course"""
        params = {'courses[0][id]': course_id}
        if fullname is not None:
            params['courses[0][fullname]'] = fullname
        if shortname is not None:
            params['courses[0][shortname]'] = shortname
        if summary is not None:
            params['courses[0][summary]'] = summary
        if visible is not None:
            params['courses[0][visible]'] = 1 if visible else 0
        
        data = self._make_request(self.CORE_COURSE_UPDATE_COURSES, params)
        return data is not None
    
    def delete_course(self, course_id: int) -> bool:
        """Delete a course"""
        params = {'courseids[0]': course_id}
        data = self._make_request(self.CORE_COURSE_DELETE_COURSES, params)
        return data is not None
    
    def duplicate_course(self, course_id: int, fullname: str, shortname: str,
                        category_id: int = None, visible: bool = True) -> Optional[Dict[str, Any]]:
        """Duplicate a course"""
        params = {
            'courseid': course_id,
            'fullname': fullname,
            'shortname': shortname,
            'visible': 1 if visible else 0
        }
        if category_id is not None:
            params['categoryid'] = category_id
        
        data = self._make_request(self.CORE_COURSE_DUPLICATE_COURSE, params)
        return data
    
    def get_course_content(self, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get course content by course ID"""
        params = {'courseid': course_id}
        data = self._make_request(self.CORE_COURSE_GET_CONTENTS, params)
        return data if data is not None else None
    
    # === Backup & Restore Management ===
    def submit_backup(self, course_id: int, 
                     settings: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Submit a backup request for a course
        
        Args:
            course_id: ID of the course to backup
            settings: Backup settings dictionary with options like:
                - activities: bool (include activities)
                - blocks: bool (include blocks)
                - filters: bool (include filters)
                - users: bool (include users)
                - role_assignments: bool (include role assignments)
                - comments: bool (include comments)
                - completion_information: bool (include completion info)
                - logs: bool (include logs)
                - grade_histories: bool (include grade histories)
        
        Returns:
            Dictionary with backup operation details including backup_id
        """
        params = {
            'courseid': course_id
        }
        
        # Add backup settings if provided
        if settings:
            backup_settings = {
                'activities': settings.get('activities', True),
                'blocks': settings.get('blocks', True),
                'filters': settings.get('filters', True),
                'users': settings.get('users', False),
                'role_assignments': settings.get('role_assignments', False),
                'comments': settings.get('comments', False),
                'completion_information': settings.get('completion_information', False),
                'logs': settings.get('logs', False),
                'grade_histories': settings.get('grade_histories', False)
            }
            
            # Convert settings to Moodle format
            for key, value in backup_settings.items():
                params[f'settings[{key}]'] = 1 if value else 0
        
        data = self._make_request(self.CORE_BACKUP_SUBMIT_BACKUP, params)
        return data
    
    def get_backup_status(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a backup operation
        
        Args:
            backup_id: ID of the backup operation
            
        Returns:
            Dictionary with backup status including progress and file information
        """
        params = {
            'backupid': backup_id
        }
        
        data = self._make_request(self.CORE_BACKUP_GET_BACKUP, params)
        return data
    
    def submit_restore(self, backup_file_path: str, target_course_id: int,
                      settings: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Submit a restore request from a backup file
        
        Args:
            backup_file_path: Path to the backup file
            target_course_id: ID of the course to restore to (0 for new course)
            settings: Restore settings dictionary with options like:
                - activities: bool (restore activities)
                - blocks: bool (restore blocks)
                - filters: bool (restore filters)
                - users: bool (restore users)
                - role_assignments: bool (restore role assignments)
                - comments: bool (restore comments)
                - completion_information: bool (restore completion info)
                - logs: bool (restore logs)
                - grade_histories: bool (restore grade histories)
        
        Returns:
            Dictionary with restore operation details
        """
        params = {
            'targetcourseid': target_course_id,
            'backupfile': backup_file_path
        }
        
        # Add restore settings if provided
        if settings:
            restore_settings = {
                'activities': settings.get('activities', True),
                'blocks': settings.get('blocks', True),
                'filters': settings.get('filters', True),
                'users': settings.get('users', False),
                'role_assignments': settings.get('role_assignments', False),
                'comments': settings.get('comments', False),
                'completion_information': settings.get('completion_information', False),
                'logs': settings.get('logs', False),
                'grade_histories': settings.get('grade_histories', False)
            }
            
            # Convert settings to Moodle format
            for key, value in restore_settings.items():
                params[f'settings[{key}]'] = 1 if value else 0
        
        data = self._make_request(self.CORE_RESTORE_SUBMIT_RESTORE, params)
        return data
    
    # === User Management ===
    def get_users(self, criteria: List[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
        """Get users based on criteria"""
        params = {}
        if criteria:
            params['criteria'] = json.dumps(criteria)
        
        data = self._make_request(self.CORE_USER_GET_USERS, params)
        return data if data is not None else None
    
    def get_user_by_field(self, field: str, value: str) -> Optional[Dict[str, Any]]:
        """Get user by field (id, username, email, etc.)"""
        params = {
            'field': field,
            'values[0]': value
        }
        
        data = self._make_request(self.CORE_USER_GET_USERS_BY_FIELD, params)
        return data[0] if data and len(data) > 0 else None
    
    def create_user(self, username: str, password: str, firstname: str, lastname: str,
                   email: str, auth: str = "manual", idnumber: str = "",
                   phone1: str = "", phone2: str = "", institution: str = "",
                   department: str = "", address: str = "", city: str = "",
                   country: str = "", lang: str = "en", timezone: str = "99",
                   mailformat: int = 1, description: str = "",
                   preferences: List[Dict] = None) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        params = {
            'users[0][username]': username,
            'users[0][password]': password,
            'users[0][firstname]': firstname,
            'users[0][lastname]': lastname,
            'users[0][email]': email,
            'users[0][auth]': auth,
            'users[0][idnumber]': idnumber,
            'users[0][phone1]': phone1,
            'users[0][phone2]': phone2,
            'users[0][institution]': institution,
            'users[0][department]': department,
            'users[0][address]': address,
            'users[0][city]': city,
            'users[0][country]': country,
            'users[0][lang]': lang,
            'users[0][timezone]': timezone,
            'users[0][mailformat]': mailformat,
            'users[0][description]': description
        }
        
        data = self._make_request(self.CORE_USER_CREATE_USERS, params)
        return data[0] if data and len(data) > 0 else None
    
    def create_users_batch(self, users: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """Create multiple users in batch"""
        params = {}
        for i, user in enumerate(users):
            for key, value in user.items():
                params[f'users[{i}][{key}]'] = value
        
        data = self._make_request(self.CORE_USER_CREATE_USERS, params)
        return data
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        params = {'users[0][id]': user_id}
        for key, value in kwargs.items():
            params[f'users[0][{key}]'] = value
        
        data = self._make_request(self.CORE_USER_UPDATE_USERS, params)
        return data is not None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        params = {'userids[0]': user_id}
        data = self._make_request(self.CORE_USER_DELETE_USERS, params)
        return data is not None
    
    def delete_users_batch(self, user_ids: List[int]) -> bool:
        """Delete multiple users"""
        params = {}
        for i, user_id in enumerate(user_ids):
            params[f'userids[{i}]'] = user_id
        
        data = self._make_request(self.CORE_USER_DELETE_USERS, params)
        return data is not None
    
    # === Enrollment Management ===
    def get_enrolled_users_by_course_id(self, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get enrolled users by course ID"""
        params = {'courseid': course_id}
        data = self._make_request(self.CORE_ENROL_GET_ENROLLED_USERS, params)
        return data if data is not None else None
    
    def get_users_courses(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get courses that a user is enrolled in"""
        params = {'userid': user_id}
        data = self._make_request(self.CORE_ENROL_GET_USERS_COURSES, params)
        return data if data is not None else None
    
    def enrol_user(self, user_id: int, course_id: int, role_id: int = 5,
                   timestart: int = None, timeend: int = None, suspend: bool = False) -> bool:
        """Enrol a user in a course"""
        params = {
            'enrolments[0][roleid]': role_id,
            'enrolments[0][userid]': user_id,
            'enrolments[0][courseid]': course_id
        }
        
        if timestart is not None:
            params['enrolments[0][timestart]'] = timestart
        if timeend is not None:
            params['enrolments[0][timeend]'] = timeend
        
        params['enrolments[0][suspend]'] = 1 if suspend else 0
        
        data = self._make_request(self.ENROL_MANUAL_ENROL_USERS, params)
        return data is not None
    
    def unenrol_user(self, user_id: int, course_id: int, role_id: int = None) -> bool:
        """Unenrol a user from a course"""
        params = {
            'enrolments[0][userid]': user_id,
            'enrolments[0][courseid]': course_id
        }
        
        if role_id is not None:
            params['enrolments[0][roleid]'] = role_id
        
        data = self._make_request(self.ENROL_MANUAL_UNENROL_USERS, params)
        return data is not None
    
    # === Group Management ===
    def get_user_groups_by_course_id(self, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get user groups by course ID"""
        params = {'courseid': course_id}
        data = self._make_request(self.CORE_GROUP_GET_COURSE_GROUPS, params)
        return data if data is not None else None
    
    def create_group(self, course_id: int, name: str, description: str = "",
                    idnumber: str = "") -> Optional[Dict[str, Any]]:
        """Create a new group"""
        params = {
            'groups[0][courseid]': course_id,
            'groups[0][name]': name,
            'groups[0][description]': description,
            'groups[0][idnumber]': idnumber
        }
        
        data = self._make_request(self.CORE_GROUP_CREATE_GROUPS, params)
        return data[0] if data and len(data) > 0 else None
    
    def delete_group(self, group_id: int) -> bool:
        """Delete a group"""
        params = {'groupids[0]': group_id}
        data = self._make_request(self.CORE_GROUP_DELETE_GROUPS, params)
        return data is not None
    
    def add_group_members(self, group_id: int, user_ids: List[int]) -> bool:
        """Add members to a group"""
        params = {}
        for i, user_id in enumerate(user_ids):
            params[f'members[{i}][groupid]'] = group_id
            params[f'members[{i}][userid]'] = user_id
        
        data = self._make_request(self.CORE_GROUP_ADD_GROUP_MEMBERS, params)
        return data is not None
    
    def remove_group_members(self, group_id: int, user_ids: List[int]) -> bool:
        """Remove members from a group"""
        params = {}
        for i, user_id in enumerate(user_ids):
            params[f'members[{i}][groupid]'] = group_id
            params[f'members[{i}][userid]'] = user_id
        
        data = self._make_request(self.CORE_GROUP_DELETE_GROUP_MEMBERS, params)
        return data is not None
    
    def get_group_members(self, group_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get group members"""
        params = {'groupids[0]': group_id}
        data = self._make_request(self.CORE_GROUP_GET_GROUP_MEMBERS, params)
        return data if data is not None else None
    
    # === Gradebook Management ===
    def get_grade_items(self, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get grade items for a course"""
        params = {'courseid': course_id}
        data = self._make_request(self.CORE_GRADE_GET_GRADE_ITEMS, params)
        return data if data is not None else None
    
    def get_grades(self, course_id: int, user_id: int = None) -> Optional[List[Dict[str, Any]]]:
        """Get grades for a course (optionally for a specific user)"""
        params = {'courseid': course_id}
        if user_id:
            params['userid'] = user_id
            
        data = self._make_request(self.CORE_GRADE_GET_GRADES, params)
        return data if data is not None else None
    
    def update_grades(self, course_id: int, grade_items: List[Dict[str, Any]]) -> bool:
        """Update grades for a course"""
        params = {'component': 'mod_assign', 'activityid': 0}
        
        for i, item in enumerate(grade_items):
            params[f'grades[{i}][itemid]'] = item.get('itemid', 0)
            params[f'grades[{i}][userid]'] = item.get('userid', 0)
            params[f'grades[{i}][grade]'] = item.get('grade', 0)
            if 'feedback' in item:
                params[f'grades[{i}][feedback]'] = item['feedback']
        
        data = self._make_request(self.CORE_GRADE_UPDATE_GRADES, params)
        return data is not None
    
    # === Role Management ===
    def get_roles(self) -> Optional[List[Dict[str, Any]]]:
        """Get all available roles"""
        data = self._make_request(self.CORE_ROLE_GET_ROLES)
        return data if data is not None else None
    
    def assign_role(self, user_id: int, role_id: int, context_id: int,
                   context_level: str = 'course') -> bool:
        """Assign a role to a user"""
        params = {
            'assignments[0][roleid]': role_id,
            'assignments[0][userid]': user_id,
            'assignments[0][contextid]': context_id,
            'assignments[0][contextlevel]': context_level
        }
        
        data = self._make_request(self.CORE_ROLE_ASSIGN_ROLES, params)
        return data is not None
    
    def unassign_role(self, user_id: int, role_id: int, context_id: int,
                     context_level: str = 'course') -> bool:
        """Unassign a role from a user"""
        params = {
            'unassignments[0][roleid]': role_id,
            'unassignments[0][userid]': user_id,
            'unassignments[0][contextid]': context_id,
            'unassignments[0][contextlevel]': context_level
        }
        
        data = self._make_request(self.CORE_ROLE_UNASSIGN_ROLES, params)
        return data is not None
    
    # === Activity Management ===
    def get_assignment_submissions(self, assignment_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get assignment submissions"""
        params = {'assignmentids[0]': assignment_id}
        data = self._make_request(self.MOD_ASSIGN_GET_SUBMISSIONS, params)
        return data if data is not None else None
    
    def get_assignment_submission_status(self, assignment_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Get assignment submission status"""
        params = {'assignmentid': assignment_id}
        if user_id:
            params['userid'] = user_id
        
        data = self._make_request(self.MOD_ASSIGN_GET_SUBMISSION_STATUS, params)
        return data
    
    def get_quiz_attempts(self, quiz_id: int, user_id: int = None) -> Optional[List[Dict[str, Any]]]:
        """Get quiz attempts"""
        params = {'quizid': quiz_id}
        if user_id:
            params['userid'] = user_id
        
        data = self._make_request(self.MOD_QUIZ_GET_USER_ATTEMPTS, params)
        return data if data is not None else None
    
    # === Course Content (duplicate method removal) ===
    def get_course_content(self, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get course content by course ID"""
        params = {'courseid': course_id}
        data = self._make_request(self.CORE_COURSE_GET_CONTENTS, params)
        return data if data is not None else None
    
    def get_users_grade_book(self, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get grade book for a course"""
        params = {'courseid': course_id}
        data = self._make_request(self.CORE_GRADE_GET_GRADE_ITEMS, params)
        return data if data is not None else None
    
    def get_group_members(self, group_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get group members"""
        params = {'groupids[]': [group_id]}
        data = self._make_request(self.CORE_GROUP_GET_GROUP_MEMBERS, params)
        return data if data is not None else None
    
    def get_grades(self, course_id: int, user_id: int = None) -> Optional[List[Dict[str, Any]]]:
        """Get grades for a course (optionally for a specific user)"""
        params = {'courseid': course_id}
        if user_id:
            params['userid'] = user_id
            
        data = self._make_request(self.CORE_GRADE_GET_GRADES, params)
        return data if data is not None else None
    
    def download_file(self, file_url: str, save_path: str) -> bool:
        """Download a file from Moodle"""
        if not self.is_connected():
            print("Not connected to Moodle")
            return False
            
        try:
            # Add token to the URL
            if '?' in file_url:
                file_url += f"&token={self.token}"
            else:
                file_url += f"?token={self.token}"
            
            response = self.session.get(file_url, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded {file_url} to {save_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Download error: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test the connection by getting site info"""
        try:
            # Try to get site info
            response = self.session.get(f"{self.host}/login/index.php")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    # === Messaging ===
    def send_instant_message(self, user_id: int, message: str, 
                           message_format: str = 'MOODLE') -> Optional[Dict[str, Any]]:
        """Send an instant message to a user"""
        params = {
            'touserid': user_id,
            'text': message,
            'textformat': message_format
        }
        
        data = self._make_request(self.CORE_MESSAGE_SEND_INSTANT_MESSAGE, params)
        return data
    
    def get_messages(self, user_id: int = None, read: bool = None,
                    type: str = None, useridfrom: int = None) -> Optional[List[Dict[str, Any]]]:
        """Get messages for a user"""
        params = {}
        if user_id:
            params['useridto'] = user_id
        if read is not None:
            params['read'] = 1 if read else 0
        if type:
            params['type'] = type
        if useridfrom:
            params['useridfrom'] = useridfrom
        
        data = self._make_request(self.CORE_MESSAGE_GET_MESSAGES, params)
        return data if data is not None else None
    
    # === File Handling ===
    def upload_file(self, filepath: str, filename: str, 
                   context_id: int = 1, component: str = 'user',
                   file_area: str = 'private', item_id: int = 0) -> Optional[Dict[str, Any]]:
        """Upload a file to Moodle"""
        import os
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            files = {
                'file': (filename, f, 'application/octet-stream')
            }
            
            params = {
                'contextid': context_id,
                'component': component,
                'filearea': file_area,
                'itemid': item_id,
                'filename': filename,
                'filepath': '/'
            }
            
            data = self._make_request(self.CORE_FILES_UPLOAD, params, files=files)
            return data
    
    def get_files(self, context_id: int = 1, component: str = 'user',
                 file_area: str = 'private', item_id: int = 0) -> Optional[List[Dict[str, Any]]]:
        """Get files from Moodle"""
        params = {
            'contextid': context_id,
            'component': component,
            'filearea': file_area,
            'itemid': item_id
        }
        
        data = self._make_request(self.CORE_FILES_GET_FILES, params)
        return data if data is not None else None
    
    def upload_user_picture(self, user_id: int, picture_filepath: str, overwrite: bool = True) -> Optional[Dict[str, Any]]:
        """Upload user profile picture
        
        Args:
            user_id: ID of the user to upload picture for
            picture_filepath: Path to the picture file
            overwrite: Whether to overwrite existing picture
            
        Returns:
            Dictionary with upload result
        """
        import os
        
        if not os.path.exists(picture_filepath):
            raise FileNotFoundError(f"Picture file not found: {picture_filepath}")
        
        # Get file extension and validate image type
        filename = os.path.basename(picture_filepath)
        file_ext = os.path.splitext(filename)[1].lower()
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        if file_ext not in valid_extensions:
            raise ValueError(f"Invalid image format. Supported formats: {', '.join(valid_extensions)}")
        
        # User context ID for profile pictures
        # In Moodle, user context ID is typically user_id + constant offset
        user_context_id = user_id
        
        with open(picture_filepath, 'rb') as f:
            files = {
                'file': (filename, f, 'image/jpeg' if file_ext in ['.jpg', '.jpeg'] else 'image/png')
            }
            
            params = {
                'contextid': user_context_id,
                'component': 'user',
                'filearea': 'private',  # User private files area
                'itemid': 0,  # User profile picture item ID
                'filename': f"profile{file_ext}",  # Moodle expects profile.jpg or profile.png
                'filepath': '/'
            }
            
            data = self._make_request(self.CORE_FILES_UPLOAD, params, files=files)
            return data
    
    # === Calendar Management ===
    def get_calendar_events(self, events_type: str = 'all', 
                           user_id: int = None, course_id: int = None,
                           group_id: int = None, category_id: int = None,
                           time_start: int = None, time_end: int = None) -> Optional[List[Dict[str, Any]]]:
        """Get calendar events"""
        params = {'events[0][eventtype]': events_type}
        
        if user_id:
            params['events[0][userid]'] = user_id
        if course_id:
            params['events[0][courseid]'] = course_id
        if group_id:
            params['events[0][groupid]'] = group_id
        if category_id:
            params['events[0][categoryid'] = category_id
        if time_start:
            params['events[0][timestart]'] = time_start
        if time_end:
            params['events[0][timeend]'] = time_end
        
        data = self._make_request(self.CORE_CALENDAR_GET_CALENDAR_EVENTS, params)
        return data if data is not None else None
    
    def create_calendar_event(self, name: str, description: str, 
                            event_type: str = 'user', 
                            course_id: int = None, group_id: int = None,
                            category_id: int = None, time_start: int = None,
                            time_end: int = None, duration: int = 0) -> Optional[Dict[str, Any]]:
        """Create a calendar event"""
        params = {
            'events[0][name]': name,
            'events[0][description]': description,
            'events[0][eventtype]': event_type,
            'events[0][duration]': duration
        }
        
        if course_id:
            params['events[0][courseid]'] = course_id
        if group_id:
            params['events[0][groupid]'] = group_id
        if category_id:
            params['events[0][categoryid'] = category_id
        if time_start:
            params['events[0][timestart]'] = time_start
        if time_end:
            params['events[0][timeend]'] = time_end
        
        data = self._make_request(self.CORE_CALENDAR_CREATE_CALENDAR_EVENTS, params)
        return data[0] if data and len(data) > 0 else None
    
    def delete_calendar_event(self, event_id: int) -> bool:
        """Delete a calendar event"""
        params = {'events[0][eventid]': event_id}
        data = self._make_request(self.CORE_CALENDAR_DELETE_CALENDAR_EVENTS, params)
        return data is not None
    
    # === Cohort Management ===
    def create_cohort(self, name: str, idnumber: str = "", 
                     description: str = "", category_id: int = 0) -> Optional[Dict[str, Any]]:
        """Create a new cohort"""
        params = {
            'cohorts[0][name]': name,
            'cohorts[0][idnumber]': idnumber,
            'cohorts[0][description]': description,
            'cohorts[0][categoryid]': category_id
        }
        
        data = self._make_request(self.CORE_COHORT_CREATE_COHORTS, params)
        return data[0] if data and len(data) > 0 else None
    
    def delete_cohort(self, cohort_id: int) -> bool:
        """Delete a cohort"""
        params = {'cohortids[0]': cohort_id}
        data = self._make_request(self.CORE_COHORT_DELETE_COHORTS, params)
        return data is not None
    
    def add_cohort_members(self, cohort_id: int, user_ids: List[int]) -> bool:
        """Add members to a cohort"""
        params = {}
        for i, user_id in enumerate(user_ids):
            params[f'members[{i}][cohortid]'] = cohort_id
            params[f'members[{i}][userid]'] = user_id
        
        data = self._make_request(self.CORE_COHORT_ADD_COHORT_MEMBERS, params)
        return data is not None
    
    # === Backup and Restore ===
    def submit_backup(self, course_id: int, settings: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Submit a backup request for a course"""
        params = {
            'courseid': course_id,
            'settings[activities]': 1,
            'settings[blocks]': 1,
            'settings[filters]': 1,
            'settings[users]': 0,
            'settings[role_assignments]': 0,
            'settings[comments]': 0,
            'settings[userscompletion]': 0,
            'settings[logs]': 0,
            'settings[grade_histories]': 0
        }
        
        if settings:
            for key, value in settings.items():
                params[f'settings[{key}]'] = value
        
        data = self._make_request(self.CORE_BACKUP_SUBMIT_BACKUP, params)
        return data
    
    def get_backup_status(self, backup_id: int) -> Optional[Dict[str, Any]]:
        """Get backup status"""
        params = {'backupid': backup_id}
        data = self._make_request(self.CORE_BACKUP_GET_BACKUP, params)
        return data
    
    def submit_restore(self, backup_file: str, target_course_id: int, 
                      settings: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Submit a restore request"""
        params = {
            'backupfile': backup_file,
            'targetcourseid': target_course_id,
            'settings[activities]': 1,
            'settings[blocks]': 1,
            'settings[filters]': 1,
            'settings[users]': 0,
            'settings[role_assignments]': 0,
            'settings[comments]': 0,
            'settings[userscompletion]': 0,
            'settings[logs]': 0,
            'settings[grade_histories]': 0
        }
        
        if settings:
            for key, value in settings.items():
                params[f'settings[{key}]'] = value
        
        data = self._make_request(self.CORE_RESTORE_SUBMIT_RESTORE, params)
        return data
    
    # === Async Backup Functions ===
    def get_async_backup_links_backup(self, backup_id: int) -> Optional[Dict[str, Any]]:
        """Get data to use when updating the status table row in the UI for when an async backup completes"""
        params = {'backupid': backup_id}
        data = self._make_request(self.CORE_BACKUP_GET_ASYNC_BACKUP_LINKS_BACKUP, params)
        return data
    
    def submit_copy_form(self, course_id: int, target_course_id: int, 
                        fullname: str = None, shortname: str = None,
                        category_id: int = None, visible: int = 1,
                       startdate: int = None, enddate: int = None,
                        options: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Handles ajax submission of course copy form"""
        params = {
            'courseid': course_id,
            'targetcourseid': target_course_id,
            'fullname': fullname,
            'shortname': shortname,
            'categoryid': category_id,
            'visible': visible
        }
        
        if startdate is not None:
            params['startdate'] = startdate
        if enddate is not None:
            params['enddate'] = enddate
        
        if options:
            for key, value in options.items():
                params[f'options[{key}]'] = value
        
        data = self._make_request(self.CORE_BACKUP_SUBMIT_COPY_FORM, params)
        return data
    
    # === Course Content Functions ===
    def get_course_content_items(self, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """Fetch all the content items (activities, resources and their subtypes) for the activity picker"""
        params = {'courseid': course_id}
        data = self._make_request(self.CORE_COURSE_GET_COURSE_CONTENT_ITEMS, params)
        return data if data is not None else None
    
    # === User Profile Functions ===
    def get_course_user_profiles(self, course_id: int, user_ids: List[int] = None) -> Optional[List[Dict[str, Any]]]:
        """Get course user profiles (each of the profiles matching a course id and a user id)"""
        params = {'courseid': course_id}
        
        if user_ids:
            for i, user_id in enumerate(user_ids):
                params[f'userids[{i}]'] = user_id
        
        data = self._make_request(self.CORE_USER_GET_COURSE_USER_PROFILES, params)
        return data if data is not None else None
    
    def get_user_preferences(self, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Return user preferences"""
        params = {}
        if user_id is not None:
            params['userid'] = user_id
        
        data = self._make_request(self.CORE_USER_GET_USER_PREFERENCES, params)
        return data if data is not None else None
    
    # === Grade Report Functions ===
    def get_user_grade_items(self, course_id: int, user_id: int, 
                           group_id: int = None) -> Optional[List[Dict[str, Any]]]:
        """Returns the complete list of grade items for users in a course"""
        params = {
            'courseid': course_id,
            'userid': user_id
        }
        
        if group_id is not None:
            params['groupid'] = group_id
        
        data = self._make_request(self.GRADEREPORT_USER_GET_GRADE_ITEMS, params)
        return data if data is not None else None
