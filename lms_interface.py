"""
LMS Interface Classes
Python implementation of the LMS interface definitions
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IGradeItem(ABC):
    """Interface for grade items"""
    
    @abstractmethod
    def get_item_name(self) -> str:
        """Get the name of the grade item"""
        pass
    
    @property
    def item_name(self) -> str:
        """Property for item name"""
        return self.get_item_name()


class IUsersGroup(ABC):
    """Interface for user groups"""
    
    @abstractmethod
    def get_filter_content(self) -> str:
        """Get filter content for the group"""
        pass
    
    @abstractmethod
    def get_group_name(self) -> str:
        """Get the group name"""
        pass
    
    @abstractmethod
    def get_id(self) -> int:
        """Get the group ID"""
        pass
    
    @abstractmethod
    def get_users_in_group(self) -> List['IUser']:
        """Get list of users in the group"""
        pass
    
    @abstractmethod
    def set_group_name(self, value: str):
        """Set the group name"""
        pass
    
    @abstractmethod
    def set_id(self, value: int):
        """Set the group ID"""
        pass
    
    @abstractmethod
    def set_users_in_group(self, value: List['IUser']):
        """Set the list of users in the group"""
        pass
    
    # Properties
    filter_content = property(get_filter_content)
    group_name = property(get_group_name, set_group_name)
    id = property(get_id, set_id)
    users_in_group = property(get_users_in_group, set_users_in_group)


class IUser(ABC):
    """Interface for users"""
    
    @abstractmethod
    def get_course(self) -> 'ICourse':
        """Get the course this user belongs to"""
        pass
    
    @abstractmethod
    def get_email(self) -> str:
        """Get user email"""
        pass
    
    @abstractmethod
    def get_filter_content(self) -> str:
        """Get filter content for the user"""
        pass
    
    @abstractmethod
    def get_first_name(self) -> str:
        """Get user first name"""
        pass
    
    @abstractmethod
    def get_full_name(self) -> str:
        """Get user full name"""
        pass
    
    @abstractmethod
    def get_id(self) -> int:
        """Get user ID"""
        pass
    
    @abstractmethod
    def get_last_name(self) -> str:
        """Get user last name"""
        pass
    
    @abstractmethod
    def get_lms(self) -> Optional['ILMS']:
        """Get the LMS instance"""
        pass
    
    @abstractmethod
    def get_roles(self) -> List[str]:
        """Get user roles"""
        pass
    
    @abstractmethod
    def set_course(self, value: 'ICourse'):
        """Set the course this user belongs to"""
        pass
    
    @abstractmethod
    def set_email(self, value: str):
        """Set user email"""
        pass
    
    @abstractmethod
    def set_first_name(self, value: str):
        """Set user first name"""
        pass
    
    @abstractmethod
    def set_last_name(self, value: str):
        """Set user last name"""
        pass
    
    @abstractmethod
    def set_lms(self, value: Optional['ILMS']):
        """Set the LMS instance"""
        pass
    
    @abstractmethod
    def set_roles(self, value: List[str]):
        """Set user roles"""
        pass
    
    # Properties
    course = property(get_course, set_course)
    email = property(get_email, set_email)
    filter_content = property(get_filter_content)
    first_name = property(get_first_name, set_first_name)
    full_name = property(get_full_name)
    id = property(get_id)
    last_name = property(get_last_name, set_last_name)
    lms = property(get_lms, set_lms)
    roles = property(get_roles, set_roles)


class ICourse(ABC):
    """Interface for courses"""
    
    @abstractmethod
    def get_category(self) -> 'ICategory':
        """Get the category this course belongs to"""
        pass
    
    @abstractmethod
    def get_course_content(self) -> List['ISection']:
        """Get course content (sections)"""
        pass
    
    @abstractmethod
    def get_course_roles(self) -> List[str]:
        """Get available course roles"""
        pass
    
    @abstractmethod
    def get_enrolled_users(self) -> List[IUser]:
        """Get enrolled users"""
        pass
    
    @abstractmethod
    def get_filter_content(self) -> str:
        """Get filter content for the course"""
        pass
    
    @abstractmethod
    def get_grade_items(self) -> List[IGradeItem]:
        """Get grade items for the course"""
        pass
    
    @abstractmethod
    def get_id(self) -> int:
        """Get course ID"""
        pass
    
    @abstractmethod
    def get_lms(self) -> Optional['ILMS']:
        """Get the LMS instance"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get course name"""
        pass
    
    @abstractmethod
    def get_user_groups(self) -> List[IUsersGroup]:
        """Get user groups in the course"""
        pass
    
    @abstractmethod
    def set_category(self, value: Optional['ICategory']):
        """Set the category this course belongs to"""
        pass
    
    @abstractmethod
    def set_lms(self, value: Optional['ILMS']):
        """Set the LMS instance"""
        pass
    
    @abstractmethod
    def set_name(self, value: str):
        """Set course name"""
        pass
    
    # Properties
    category = property(get_category, set_category)
    course_content = property(get_course_content)
    course_roles = property(get_course_roles)
    enrolled_users = property(get_enrolled_users)
    filter_content = property(get_filter_content)
    grade_items = property(get_grade_items)
    id = property(get_id)
    lms = property(get_lms, set_lms)
    name = property(get_name, set_name)
    user_groups = property(get_user_groups)


class ICategory(ABC):
    """Interface for categories"""
    
    @abstractmethod
    def get_courses(self) -> List[ICourse]:
        """Get courses in this category"""
        pass
    
    @abstractmethod
    def get_filter_content(self) -> str:
        """Get filter content for the category"""
        pass
    
    @abstractmethod
    def get_id(self) -> int:
        """Get category ID"""
        pass
    
    @abstractmethod
    def get_lms(self) -> Optional['ILMS']:
        """Get the LMS instance"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get category name"""
        pass
    
    @abstractmethod
    def set_lms(self, value: Optional['ILMS']):
        """Set the LMS instance"""
        pass
    
    @abstractmethod
    def set_name(self, value: str):
        """Set category name"""
        pass
    
    # Properties
    courses = property(get_courses)
    filter_content = property(get_filter_content)
    id = property(get_id)
    lms = property(get_lms, set_lms)
    name = property(get_name, set_name)


class IModule(ABC):
    """Interface for modules"""
    
    @abstractmethod
    def get_filter_content(self) -> str:
        """Get filter content for the module"""
        pass
    
    @abstractmethod
    def get_id(self) -> int:
        """Get module ID"""
        pass
    
    @abstractmethod
    def get_mod_name(self) -> str:
        """Get module name"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get module display name"""
        pass
    
    @abstractmethod
    def get_section(self) -> 'ISection':
        """Get the section this module belongs to"""
        pass
    
    @abstractmethod
    def set_name(self, value: str):
        """Set module display name"""
        pass
    
    @abstractmethod
    def set_section(self, value: 'ISection'):
        """Set the section this module belongs to"""
        pass
    
    # Properties
    filter_content = property(get_filter_content)
    id = property(get_id)
    mod_name = property(get_mod_name)
    name = property(get_name, set_name)
    section = property(get_section, set_section)


class ISection(ABC):
    """Interface for sections"""
    
    @abstractmethod
    def get_course(self) -> Optional['ICourse']:
        """Get the course this section belongs to"""
        pass
    
    @abstractmethod
    def get_filter_content(self) -> str:
        """Get filter content for the section"""
        pass
    
    @abstractmethod
    def get_id(self) -> int:
        """Get section ID"""
        pass
    
    @abstractmethod
    def get_modules(self) -> List[IModule]:
        """Get modules in this section"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get section name"""
        pass
    
    @abstractmethod
    def set_course(self, value: Optional['ICourse']):
        """Set the course this section belongs to"""
        pass
    
    @abstractmethod
    def set_name(self, value: str):
        """Set section name"""
        pass
    
    # Properties
    course = property(get_course, set_course)
    filter_content = property(get_filter_content)
    id = property(get_id)
    modules = property(get_modules)
    name = property(get_name, set_name)


class ILMS(ABC):
    """Interface for LMS (Learning Management System)"""
    
    @abstractmethod
    def get_categories(self) -> List[ICategory]:
        """Get all LMS categories"""
        pass
    
    @abstractmethod
    def get_courses(self) -> List[ICourse]:
        """Get all LMS courses"""
        pass
    
    @abstractmethod
    def get_enrolled_courses(self) -> List[ICourse]:
        """Get courses the current user is enrolled in"""
        pass
    
    @abstractmethod
    def get_filter_content(self) -> str:
        """Get filter content for the LMS"""
        pass
    
    @abstractmethod
    def get_host(self) -> str:
        """Get LMS host URL"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get LMS name"""
        pass
    
    @abstractmethod
    def get_token(self) -> str:
        """Get authentication token"""
        pass
    
    @abstractmethod
    def get_user(self) -> IUser:
        """Get current user"""
        pass
    
    @abstractmethod
    def set_host(self, value: str):
        """Set LMS host URL"""
        pass
    
    @abstractmethod
    def set_name(self, value: str):
        """Set LMS name"""
        pass
    
    @abstractmethod
    def set_token(self, value: str):
        """Set authentication token"""
        pass
    
    @abstractmethod
    def connect(self, username: str, password: str, service: str = "moodle_mobile_app") -> bool:
        """Connect to the LMS"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to LMS"""
        pass
    
    # Properties
    categories = property(get_categories)
    courses = property(get_courses)
    enrolled_courses = property(get_enrolled_courses)
    filter_content = property(get_filter_content)
    host = property(get_host, set_host)
    name = property(get_name, set_name)
    token = property(get_token, set_token)
    user = property(get_user)


class IContent(ABC):
    """Interface for content files"""
    
    @abstractmethod
    def get_file_name(self) -> str:
        """Get the file name"""
        pass
    
    @abstractmethod
    def get_file_type(self) -> str:
        """Get the file type"""
        pass
    
    @abstractmethod
    def get_mime_type(self) -> str:
        """Get the MIME type"""
        pass
    
    @abstractmethod
    def get_file_url(self) -> str:
        """Get the file URL"""
        pass
    
    @abstractmethod
    def get_module(self) -> 'IModule':
        """Get the module this content belongs to"""
        pass
    
    @abstractmethod
    def set_file_name(self, value: str):
        """Set the file name"""
        pass
    
    @abstractmethod
    def set_file_type(self, value: str):
        """Set the file type"""
        pass
    
    @abstractmethod
    def set_mime_type(self, value: str):
        """Set the MIME type"""
        pass
    
    @abstractmethod
    def set_file_url(self, value: str):
        """Set the file URL"""
        pass
    
    # Properties
    file_name = property(get_file_name, set_file_name)
    file_type = property(get_file_type, set_file_type)
    mime_type = property(get_mime_type, set_mime_type)
    file_url = property(get_file_url, set_file_url)
    module = property(get_module)


class LMSInterface(ILMS):
    """Concrete implementation of LMS interface"""
    
    def __init__(self):
        self._host = ""
        self._name = ""
        self._token = ""
        self._user = None
        self._categories = []
        self._courses = []
        self._enrolled_courses = []
        
    def get_categories(self) -> List[ICategory]:
        return self._categories
    
    def get_courses(self) -> List[ICourse]:
        return self._courses
    
    def get_enrolled_courses(self) -> List[ICourse]:
        return self._enrolled_courses
    
    def get_filter_content(self) -> str:
        return self._name
    
    def get_host(self) -> str:
        return self._host
    
    def get_name(self) -> str:
        return self._name
    
    def get_token(self) -> str:
        return self._token
    
    def get_user(self) -> IUser:
        return self._user
    
    def set_host(self, value: str):
        self._host = value
    
    def set_name(self, value: str):
        self._name = value
    
    def set_token(self, value: str):
        self._token = value
    
    def connect(self, username: str, password: str, service: str = "moodle_mobile_app") -> bool:
        # This will be implemented with the REST API client
        return False
    
    def is_connected(self) -> bool:
        return self._token != ""
