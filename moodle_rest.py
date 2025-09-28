"""
Moodle REST API Client
Python implementation of the Moodle REST API integration
"""

import requests
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin


class MoodleRestClient:
    """Moodle REST API client"""
    
    # Moodle Web Service Functions
    CORE_USER_GET_USERS = "core_user_get_users"
    CORE_USER_GET_USERS_BY_FIELD = "core_user_get_users_by_field"
    CORE_COURSE_GET_COURSES = "core_course_get_courses"
    CORE_COURSE_GET_CATEGORIES = "core_course_get_categories"
    CORE_COURSE_GET_CONTENTS = "core_course_get_contents"
    CORE_ENROL_GET_ENROLLED_USERS = "core_enrol_get_enrolled_users"
    CORE_ENROL_GET_USERS_COURSES = "core_enrol_get_users_courses"
    CORE_GROUP_GET_COURSE_GROUPS = "core_group_get_course_groups"
    CORE_GROUP_GET_GROUP_MEMBERS = "core_group_get_group_members"
    CORE_GRADE_GET_GRADE_ITEMS = "core_grade_get_grade_items"
    CORE_GRADE_GET_GRADES = "core_grade_get_grades"
    
    def __init__(self, host: str, username: str = "", password: str = "", service: str = "moodle_mobile_app"):
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.service = service
        self.token = ""
        self.session = requests.Session()
        
    def connect(self) -> bool:
        """Connect to Moodle and get authentication token"""
        try:
            # Moodle token endpoint
            token_url = f"{self.host}/login/token.php"
            
            params = {
                'username': self.username,
                'password': self.password,
                'service': self.service
            }
            
            response = self.session.post(token_url, data=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'token' in data:
                self.token = data['token']
                return True
            else:
                print(f"Connection failed: {data.get('error', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to Moodle"""
        return self.token != ""
    
    def _make_request(self, function: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make a REST API request to Moodle"""
        if not self.is_connected():
            print("Not connected to Moodle")
            return None
            
        try:
            # Moodle web service endpoint
            ws_url = f"{self.host}/webservice/rest/server.php"
            
            request_params = {
                'wstoken': self.token,
                'wsfunction': function,
                'moodlewsrestformat': 'json'
            }
            
            if params:
                request_params.update(params)
            
            response = self.session.post(ws_url, data=request_params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for Moodle errors
            if isinstance(data, dict) and 'exception' in data:
                print(f"Moodle error: {data.get('message', 'Unknown error')}")
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
    
    def get_categories(self) -> Optional[List[Dict[str, Any]]]:
        """Get all categories"""
        data = self._make_request(self.CORE_COURSE_GET_CATEGORIES)
        return data if data is not None else None
    
    def get_courses(self) -> Optional[List[Dict[str, Any]]]:
        """Get all courses"""
        data = self._make_request(self.CORE_COURSE_GET_COURSES)
        return data if data is not None else None
    
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
    
    def get_user_groups_by_course_id(self, course_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get user groups by course ID"""
        params = {'courseid': course_id}
        data = self._make_request(self.CORE_GROUP_GET_COURSE_GROUPS, params)
        return data if data is not None else None
    
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
            'values': [value]
        }
        
        data = self._make_request(self.CORE_USER_GET_USERS_BY_FIELD, params)
        return data[0] if data and len(data) > 0 else None
    
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
