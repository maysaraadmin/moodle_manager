"""
Data Model Classes for LMS Explorer
Concrete implementations of the LMS interface classes
"""

from typing import List, Optional
from lms_interface import (ILMS, IUser, ICourse, ICategory, IModule, ISection, 
                           IGradeItem, IUsersGroup, IContent)


class GradeItem(IGradeItem):
    """Concrete implementation of grade item"""
    
    def __init__(self, item_name: str = ""):
        self._item_name = item_name
    
    def get_item_name(self) -> str:
        return self._item_name
    
    def set_item_name(self, value: str):
        self._item_name = value


class UsersGroup(IUsersGroup):
    """Concrete implementation of user group"""
    
    def __init__(self, group_name: str = "", group_id: int = 0):
        self._group_name = group_name
        self._id = group_id
        self._users_in_group: List[IUser] = []
        self._filter_content = ""
    
    def get_filter_content(self) -> str:
        if not self._filter_content:
            self._filter_content = f"{self._group_name} {self._id}"
        return self._filter_content
    
    def get_group_name(self) -> str:
        return self._group_name
    
    def get_id(self) -> int:
        return self._id
    
    def get_users_in_group(self) -> List[IUser]:
        return self._users_in_group
    
    def set_group_name(self, value: str):
        self._group_name = value
        self._filter_content = ""  # Reset filter content
    
    def set_id(self, value: int):
        self._id = value
        self._filter_content = ""  # Reset filter content
    
    def set_users_in_group(self, value: List[IUser]):
        self._users_in_group = value


class User(IUser):
    """Concrete implementation of user"""
    
    def __init__(self, user_id: int = 0, first_name: str = "", last_name: str = "", 
                 email: str = ""):
        self._id = user_id
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._username = ""
        self._full_name = ""
        self._course: Optional[ICourse] = None
        self._lms: Optional[ILMS] = None
        self._roles: List[str] = []
        self._other_enrolled_courses: List[ICourse] = []
        self._last_access = ""
        self._last_access_from = ""
        self._time_created = ""
        self._time_modified = ""
        self._notes = ""
        self._filter_content = ""
    
    def get_course(self) -> Optional[ICourse]:
        return self._course
    
    def get_email(self) -> str:
        return self._email
    
    def get_filter_content(self) -> str:
        if not self._filter_content:
            self._filter_content = f"{self._first_name} {self._last_name} {self._full_name} {self._username} {self._email} {self._id}"
        return self._filter_content
    
    def get_first_name(self) -> str:
        return self._first_name
    
    def get_full_name(self) -> str:
        if self._full_name:
            return self._full_name
        return f"{self._first_name} {self._last_name}"
    
    def get_id(self) -> int:
        return self._id
    
    def get_last_name(self) -> str:
        return self._last_name
    
    def get_lms(self) -> Optional[ILMS]:
        return self._lms
    
    def get_roles(self) -> List[str]:
        return self._roles
    
    def set_course(self, value: Optional[ICourse]):
        self._course = value
    
    def set_email(self, value: str):
        self._email = value
        self._filter_content = ""  # Reset filter content
    
    def set_first_name(self, value: str):
        self._first_name = value
        self._filter_content = ""  # Reset filter content
    
    def set_last_name(self, value: str):
        self._last_name = value
        self._filter_content = ""  # Reset filter content
    
    def set_lms(self, value: Optional[ILMS]):
        self._lms = value
    
    def set_roles(self, value: List[str]):
        self._roles = value
        self._filter_content = ""  # Reset filter content
    
    def get_username(self) -> str:
        return self._username
    
    def set_username(self, value: str):
        self._username = value
        self._filter_content = ""  # Reset filter content
    
    def get_other_enrolled_courses(self) -> List[ICourse]:
        return self._other_enrolled_courses
    
    def get_last_access(self) -> str:
        return self._last_access
    
    def set_last_access(self, value: str):
        self._last_access = value
    
    def get_last_access_from(self) -> str:
        return self._last_access_from
    
    def set_last_access_from(self, value: str):
        self._last_access_from = value
    
    def get_time_created(self) -> str:
        return self._time_created
    
    def set_time_created(self, value: str):
        self._time_created = value
    
    def get_time_modified(self) -> str:
        return self._time_modified
    
    def set_time_modified(self, value: str):
        self._time_modified = value
    
    def get_notes(self) -> str:
        return self._notes
    
    def set_notes(self, value: str):
        self._notes = value
    
    # Properties to match IUser interface
    course = property(get_course, set_course)
    email = property(get_email, set_email)
    filter_content = property(get_filter_content)
    first_name = property(get_first_name, set_first_name)
    full_name = property(get_full_name)
    id = property(get_id)
    last_name = property(get_last_name, set_last_name)
    lms = property(get_lms, set_lms)
    roles = property(get_roles, set_roles)


class Module(IModule):
    """Concrete implementation of module"""
    
    def __init__(self, module_id: int = 0, mod_name: str = "", name: str = ""):
        self._id = module_id
        self._mod_name = mod_name
        self._name = name
        self._section: Optional[ISection] = None
        self._contents: List[IContent] = []
        self._mod_type = "unknow"  # Default to unknown module type
        self._filter_content = ""
    
    def get_filter_content(self) -> str:
        if not self._filter_content:
            self._filter_content = f"{self._name} {self._mod_name}"
        return self._filter_content
    
    def get_id(self) -> int:
        return self._id
    
    def get_mod_name(self) -> str:
        return self._mod_name
    
    def get_name(self) -> str:
        return self._name
    
    def get_section(self) -> Optional[ISection]:
        return self._section
    
    def set_name(self, value: str):
        self._name = value
        self._filter_content = ""  # Reset filter content
    
    def set_section(self, value: Optional[ISection]):
        self._section = value
    
    def get_contents(self) -> List[IContent]:
        return self._contents
    
    def get_mod_type(self) -> str:
        return self._mod_type
    
    def set_mod_type(self, value: str):
        self._mod_type = value
    
    def add_content(self, content: IContent):
        """Add content to this module"""
        content.set_module(self)
        self._contents.append(content)
    
    def remove_content(self, content: IContent):
        """Remove content from this module"""
        if content in self._contents:
            self._contents.remove(content)
            content.set_module(None)


class Section(ISection):
    """Concrete implementation of section"""
    
    def __init__(self, section_id: int = 0, name: str = ""):
        self._id = section_id
        self._name = name
        self._course: Optional[ICourse] = None
        self._modules: List[IModule] = []
        self._filter_content = ""
    
    def get_course(self) -> Optional[ICourse]:
        return self._course
    
    def get_filter_content(self) -> str:
        if not self._filter_content:
            self._filter_content = f"{self._name} {self._id}"
        return self._filter_content
    
    def get_id(self) -> int:
        return self._id
    
    def get_modules(self) -> List[IModule]:
        return self._modules
    
    def get_name(self) -> str:
        return self._name
    
    def set_course(self, value: Optional[ICourse]):
        self._course = value
    
    def set_name(self, value: str):
        self._name = value
        self._filter_content = ""  # Reset filter content
    
    def add_module(self, module: IModule):
        """Add a module to this section"""
        module.set_section(self)
        self._modules.append(module)
    
    def remove_module(self, module: IModule):
        """Remove a module from this section"""
        if module in self._modules:
            self._modules.remove(module)
            module.set_section(None)


class Course(ICourse):
    """Concrete implementation of course"""
    
    def __init__(self, course_id: int = 0, name: str = ""):
        self._id = course_id
        self._name = name
        self._display_name = name
        self._full_name = name
        self._short_name = ""
        self._category: Optional[ICategory] = None
        self._lms: Optional[ILMS] = None
        self._enrolled_users: List[IUser] = []
        self._user_groups: List[IUsersGroup] = []
        self._grade_items: List[IGradeItem] = []
        self._course_content: List[ISection] = []
        self._course_roles: List[str] = []
        self._group_mode = 0
        self._start_date = ""
        self._end_date = ""
        self._time_created = ""
        self._time_modified = ""
        self._filter_content = ""
    
    def get_category(self) -> Optional[ICategory]:
        return self._category
    
    def get_course_content(self) -> List[ISection]:
        return self._course_content
    
    def get_course_roles(self) -> List[str]:
        return self._course_roles
    
    def get_enrolled_users(self) -> List[IUser]:
        return self._enrolled_users
    
    def get_filter_content(self) -> str:
        if not self._filter_content:
            self._filter_content = f"{self._name} {self._id}"
        return self._filter_content
    
    def get_grade_items(self) -> List[IGradeItem]:
        return self._grade_items
    
    def get_id(self) -> int:
        return self._id
    
    def get_lms(self) -> Optional[ILMS]:
        return self._lms
    
    def get_name(self) -> str:
        return self._name
    
    def get_user_groups(self) -> List[IUsersGroup]:
        return self._user_groups
    
    def set_category(self, value: Optional[ICategory]):
        self._category = value
    
    def set_lms(self, value: Optional[ILMS]):
        self._lms = value
    
    def set_name(self, value: str):
        self._name = value
        self._filter_content = ""  # Reset filter content
    
    def add_enrolled_user(self, user: IUser):
        """Add an enrolled user to the course"""
        user.set_course(self)
        self._enrolled_users.append(user)
    
    def remove_enrolled_user(self, user: IUser):
        """Remove an enrolled user from the course"""
        if user in self._enrolled_users:
            self._enrolled_users.remove(user)
            user.set_course(None)
    
    def add_user_group(self, group: IUsersGroup):
        """Add a user group to the course"""
        self._user_groups.append(group)
    
    def remove_user_group(self, group: IUsersGroup):
        """Remove a user group from the course"""
        if group in self._user_groups:
            self._user_groups.remove(group)
    
    def add_grade_item(self, item: IGradeItem):
        """Add a grade item to the course"""
        self._grade_items.append(item)
    
    def remove_grade_item(self, item: IGradeItem):
        """Remove a grade item from the course"""
        if item in self._grade_items:
            self._grade_items.remove(item)
    
    def add_section(self, section: ISection):
        """Add a section to the course content"""
        section.set_course(self)
        self._course_content.append(section)
    
    def remove_section(self, section: ISection):
        """Remove a section from the course content"""
        if section in self._course_content:
            self._course_content.remove(section)
    
    def get_course_content(self):
        """Get course content from LMS"""
        # Placeholder implementation
        pass
    
    def get_course_roles(self, course_roles: List[str]):
        """Get course roles"""
        # Placeholder implementation
        pass
    
    def get_grade_book(self):
        """Get grade book"""
        # Placeholder implementation
        pass
    
    def get_user_count_by_role(self, role: str) -> int:
        """Get user count by role"""
        count = 0
        for user in self._enrolled_users:
            if role in user.get_roles():
                count += 1
        return count
    
    def refresh_enrolled_users(self):
        """Refresh enrolled users"""
        # Placeholder implementation
        pass
    
    def refresh_user_groups(self):
        """Refresh user groups"""
        # Placeholder implementation
        pass
    
    # Properties to match ICourse interface
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


class Category(ICategory):
    """Concrete implementation of category"""
    
    def __init__(self, category_id: int = 0, name: str = ""):
        self._id = category_id
        self._name = name
        self._lms: Optional[ILMS] = None
        self._courses: List[ICourse] = []
        self._categories: List[ICategory] = []
        self._parent_category = 0
        self._filter_content = ""
    
    def get_courses(self) -> List[ICourse]:
        return self._courses
    
    def get_filter_content(self) -> str:
        if not self._filter_content:
            self._filter_content = f"{self._name} {self._id}"
        return self._filter_content
    
    def get_id(self) -> int:
        return self._id
    
    def get_lms(self) -> Optional[ILMS]:
        return self._lms
    
    def get_name(self) -> str:
        return self._name
    
    def set_lms(self, value: Optional[ILMS]):
        self._lms = value
    
    def set_name(self, value: str):
        self._name = value
        self._filter_content = ""  # Reset filter content
    
    def add_course(self, course: ICourse):
        """Add a course to this category"""
        course.set_category(self)
        self._courses.append(course)
    
    def remove_course(self, course: ICourse):
        """Remove a course from this category"""
        if course in self._courses:
            self._courses.remove(course)
            course.set_category(None)
    
    def get_categories(self) -> List[ICategory]:
        return self._categories
    
    def get_courses_count(self) -> int:
        return len(self._courses)
    
    def get_parent_category(self) -> int:
        return self._parent_category
    
    def set_parent_category(self, value: int):
        self._parent_category = value
    
    def get_sub_categories_count(self) -> int:
        return len(self._categories)
    
    def add_category(self, category: ICategory):
        """Add a sub-category to this category"""
        self._categories.append(category)
    
    def remove_category(self, category: ICategory):
        """Remove a sub-category from this category"""
        if category in self._categories:
            self._categories.remove(category)
    
    # Properties to match ICategory interface
    courses = property(get_courses)
    filter_content = property(get_filter_content)
    id = property(get_id)
    lms = property(get_lms, set_lms)
    name = property(get_name, set_name)


class LMS(ILMS):
    """Concrete implementation of LMS"""
    
    def __init__(self, name: str = "", host: str = ""):
        self._name = name
        self._host = host
        self._token = ""
        self._user: Optional[IUser] = None
        self._categories: List[ICategory] = []
        self._courses: List[ICourse] = []
        self._enrolled_courses: List[ICourse] = []
        self._flat_courses: List[ICourse] = []
        self._auto_connect = False
        self._id = ""
        self._password = ""
        self._service = ""
        self._username = ""
        self._filter_content = ""
    
    def get_categories(self) -> List[ICategory]:
        return self._categories
    
    def get_courses(self) -> List[ICourse]:
        return self._courses
    
    def get_enrolled_courses(self) -> List[ICourse]:
        return self._enrolled_courses
    
    def get_filter_content(self) -> str:
        if not self._filter_content:
            self._filter_content = f"{self._name} {self._host}"
        return self._filter_content
    
    def get_host(self) -> str:
        return self._host
    
    def get_name(self) -> str:
        return self._name
    
    def get_token(self) -> str:
        return self._token
    
    def get_user(self) -> Optional[IUser]:
        return self._user
    
    def set_host(self, value: str):
        self._host = value
        self._filter_content = ""  # Reset filter content
    
    def set_name(self, value: str):
        self._name = value
        self._filter_content = ""  # Reset filter content
    
    def set_token(self, value: str):
        self._token = value
    
    def connect(self, username: str, password: str, service: str = "moodle_mobile_app") -> bool:
        """Connect to the LMS using Moodle REST client"""
        try:
            from moodle_rest import MoodleRestClient
            
            # Store credentials
            self._username = username
            self._password = password
            self._service = service
            
            # Create Moodle REST client
            self.moodle_client = MoodleRestClient(self._host, username, password, service)
            
            # Connect to Moodle
            if self.moodle_client.connect():
                self._token = self.moodle_client.token
                
                # Load data from Moodle
                self.load_lms_data()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def is_connected(self) -> bool:
        return self._token != ""
    
    def add_category(self, category: ICategory):
        """Add a category to the LMS"""
        category.set_lms(self)
        self._categories.append(category)
    
    def remove_category(self, category: ICategory):
        """Remove a category from the LMS"""
        if category in self._categories:
            self._categories.remove(category)
            category.set_lms(None)
    
    def add_course(self, course: ICourse):
        """Add a course to the LMS"""
        course.set_lms(self)
        self._courses.append(course)
    
    def remove_course(self, course: ICourse):
        """Remove a course from the LMS"""
        if course in self._courses:
            self._courses.remove(course)
            course.set_lms(None)
    
    def add_enrolled_course(self, course: ICourse):
        """Add an enrolled course to the LMS"""
        course.set_lms(self)
        self._enrolled_courses.append(course)
    
    def remove_enrolled_course(self, course: ICourse):
        """Remove an enrolled course from the LMS"""
        if course in self._enrolled_courses:
            self._enrolled_courses.remove(course)
            course.set_lms(None)
    
    def get_flat_courses(self) -> List[ICourse]:
        return self._flat_courses
    
    def set_flat_courses(self, courses: List[ICourse]):
        self._flat_courses = courses
    
    def get_auto_connect(self) -> bool:
        return self._auto_connect
    
    def set_auto_connect(self, value: bool):
        self._auto_connect = value
    
    def get_id(self) -> str:
        return self._id
    
    def set_id(self, value: str):
        self._id = value
    
    def get_password(self) -> str:
        return self._password
    
    def set_password(self, value: str):
        self._password = value
    
    def get_service(self) -> str:
        return self._service
    
    def set_service(self, value: str):
        self._service = value
    
    def get_username(self) -> str:
        return self._username
    
    def set_username(self, value: str):
        self._username = value
    
    def first_level_categories_count(self) -> int:
        """Get count of first level categories"""
        return len(self._categories)
    
    def load_lms_data(self):
        """Load all LMS data (categories, courses, etc.) from Moodle"""
        try:
            # Clear existing data
            self._categories.clear()
            self._courses.clear()
            self._enrolled_courses.clear()
            
            # Load categories
            self.load_categories()
            
            # Load courses
            self.load_courses()
            
            # Load enrolled courses
            self.load_enrolled_courses()
            
            print(f"Loaded {len(self._categories)} categories, {len(self._courses)} courses, {len(self._enrolled_courses)} enrolled courses")
            
        except Exception as e:
            print(f"Error loading LMS data: {e}")
    
    def load_categories(self):
        """Load categories from Moodle"""
        try:
            categories_data = self.moodle_client.get_categories()
            if categories_data:
                for cat_data in categories_data:
                    category = Category(
                        category_id=cat_data.get('id', 0),
                        name=cat_data.get('name', f"Category {cat_data.get('id', 0)}")
                    )
                    category.set_lms(self)
                    self._categories.append(category)
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    def load_courses(self):
        """Load courses from Moodle"""
        try:
            courses_data = self.moodle_client.get_courses()
            if courses_data:
                for course_data in courses_data:
                    course = Course(
                        course_id=course_data.get('id', 0),
                        name=course_data.get('fullname', f"Course {course_data.get('id', 0)}")
                    )
                    course.set_lms(self)
                    
                    # Set category if available
                    category_id = course_data.get('categoryid', 0)
                    if category_id > 0:
                        category = self.get_category_by_id(category_id)
                        if category:
                            course.set_category(category)
                            category.add_course(course)
                    else:
                        # Course without category
                        self._courses.append(course)
        except Exception as e:
            print(f"Error loading courses: {e}")
    
    def load_enrolled_courses(self):
        """Load enrolled courses for the current user"""
        try:
            # Get user info first
            user_data = self.moodle_client.get_user_by_field('username', self._username)
            if user_data:
                user_id = user_data.get('id', 0)
                if user_id > 0:
                    # Get enrolled courses using core_enrol_get_users_courses
                    enrolled_data = self.moodle_client.get_users_courses(user_id)
                    if enrolled_data:
                        for enrolled_course in enrolled_data:
                            course = Course(
                                course_id=enrolled_course.get('id', 0),
                                name=enrolled_course.get('fullname', f"Course {enrolled_course.get('id', 0)}")
                            )
                            course.set_lms(self)
                            self._enrolled_courses.append(course)
        except Exception as e:
            print(f"Error loading enrolled courses: {e}")
    
    def get_categories_from_connection(self):
        """Get categories from LMS connection (legacy method)"""
        self.load_categories()
        return self._categories
    
    def get_category_by_id(self, category_id: int) -> Optional[ICategory]:
        """Get category by ID"""
        for category in self._categories:
            if category.get_id() == category_id:
                return category
        return None
    
    def get_course_by_id(self, course_id: int) -> Optional[ICourse]:
        """Get course by ID"""
        for course in self._courses:
            if course.get_id() == course_id:
                return course
        return None
    
    def get_courses(self):
        """Get courses from LMS"""
        self.load_courses()
        return self._courses
    
    def get_users_by_almost_all_fields(self, filter_str: str) -> List[IUser]:
        """Get users by almost all fields"""
        # Placeholder implementation
        return []
    
    def download_all_course_content(self, course: ICourse):
        """Download all course content"""
        # Placeholder implementation
        pass
    
    # Properties required by ILMS interface
    categories = property(get_categories)
    courses = property(get_courses)
    enrolled_courses = property(get_enrolled_courses)
    filter_content = property(get_filter_content)
    host = property(get_host, set_host)
    name = property(get_name, set_name)
    token = property(get_token, set_token)
    user = property(get_user)


class Content(IContent):
    """Concrete implementation of content file"""
    
    def __init__(self, module: Optional['IModule'] = None):
        self._file_name = ""
        self._file_type = ""
        self._mime_type = ""
        self._file_url = ""
        self._module = module
        self._filter_content = ""
    
    def get_file_name(self) -> str:
        return self._file_name
    
    def get_file_type(self) -> str:
        return self._file_type
    
    def get_mime_type(self) -> str:
        return self._mime_type
    
    def get_file_url(self) -> str:
        return self._file_url
    
    def get_module(self) -> Optional['IModule']:
        return self._module
    
    def get_filter_content(self) -> str:
        if not self._filter_content:
            self._filter_content = f"{self._file_name} {self._file_type}"
        return self._filter_content
    
    def set_file_name(self, value: str):
        self._file_name = value
        self._filter_content = ""  # Reset filter content
    
    def set_file_type(self, value: str):
        self._file_type = value
        self._filter_content = ""  # Reset filter content
    
    def set_mime_type(self, value: str):
        self._mime_type = value
    
    def set_file_url(self, value: str):
        self._file_url = value
    
    def set_module(self, value: Optional['IModule']):
        self._module = value
    
    # Properties
    file_name = property(get_file_name, set_file_name)
    file_type = property(get_file_type, set_file_type)
    mime_type = property(get_mime_type, set_mime_type)
    file_url = property(get_file_url, set_file_url)
    module = property(get_module, set_module)
    filter_content = property(get_filter_content)


class LMSNetwork:
    """Network class for managing multiple LMS instances"""
    
    def __init__(self):
        self._lms_list: List[ILMS] = []
    
    def add(self, lms: ILMS):
        """Add an LMS instance to the network"""
        self._lms_list.append(lms)
    
    def count(self) -> int:
        """Get the number of LMS instances in the network"""
        return len(self._lms_list)
    
    def get_lms(self, index: int) -> Optional[ILMS]:
        """Get an LMS instance by index"""
        if 0 <= index < len(self._lms_list):
            return self._lms_list[index]
        return None
    
    def remove(self, index: int):
        """Remove an LMS instance by index"""
        if 0 <= index < len(self._lms_list):
            self._lms_list.pop(index)
    
    def clear(self):
        """Clear all LMS instances from the network"""
        self._lms_list.clear()
    
    def get_all_lms(self) -> List[ILMS]:
        """Get all LMS instances in the network"""
        return self._lms_list.copy()
    
    # Allow indexing access
    def __getitem__(self, index: int) -> Optional[ILMS]:
        return self.get_lms(index)
    
    def __setitem__(self, index: int, value: ILMS):
        if 0 <= index < len(self._lms_list):
            self._lms_list[index] = value
    
    def __len__(self) -> int:
        return self.count()
    
    def __iter__(self):
        return iter(self._lms_list)


# Global network instance
_global_lms_network: Optional[LMSNetwork] = None


def get_global_network() -> LMSNetwork:
    """Get the global LMS network instance"""
    global _global_lms_network
    if _global_lms_network is None:
        _global_lms_network = LMSNetwork()
    return _global_lms_network
