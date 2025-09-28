"""
Browser helper for LMS Explorer
Handles opening URLs and LMS objects in system browser
"""

import webbrowser
import os
import platform
from typing import Optional
from lms_interface import ILMS, ICategory, ICourse, IUser
from helpers.constants import *


class BrowserHelper:
    """Helper class for opening URLs and LMS objects in browser"""
    
    @staticmethod
    def open_in_browser(url: str):
        """
        Open URL in default system browser
        Args:
            url: The URL to open
        """
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open URL {url}: {e}")
    
    @staticmethod
    def open_lms_in_browser(lms: ILMS):
        """
        Open LMS instance in browser
        Args:
            lms: The LMS instance to open
        """
        if lms and lms.host:
            url = lms.host if lms.host.startswith('http') else f'https://{lms.host}'
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_category_in_browser(category: ICategory):
        """
        Open category in browser
        Args:
            category: The category to open
        """
        if category and category.lms and category.id:
            url = f"{category.lms.host}{CATEGORY_VIEW % category.id}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_course_in_browser(course: ICourse):
        """
        Open course in browser
        Args:
            course: The course to open
        """
        if course and course.lms and course.id:
            url = f"{course.lms.host}{COURSE_VIEW % course.id}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_user_in_browser(user: IUser):
        """
        Open user profile in browser
        Args:
            user: The user to open
        """
        if user and user.lms and user.id:
            url = f"{user.lms.host}{PROFILE_VIEW % user.id}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_user_in_course_in_browser(user: IUser, course: ICourse):
        """
        Open user profile in course context in browser
        Args:
            user: The user to open
            course: The course context
        """
        if user and course and user.id and course.id:
            url = f"{course.lms.host}{PROFILE_VIEW_IN_COURSE % (user.id, course.id)}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_users_in_browser_lms(lms: ILMS):
        """
        Open users page for LMS in browser
        Args:
            lms: The LMS instance
        """
        if lms and lms.host:
            url = f"{lms.host}{ADMIN_USER}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_users_in_browser_course(course: ICourse):
        """
        Open users page for course in browser
        Args:
            course: The course
        """
        if course and course.lms and course.id:
            url = f"{course.lms.host}{USERS_VIEW % course.id}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_upload_users_in_browser(lms: ILMS):
        """
        Open upload users page for LMS in browser
        Args:
            lms: The LMS instance
        """
        if lms and lms.host:
            url = f"{lms.host}{USERS_UPLOAD}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_edit_profile_in_browser(user: IUser, course: ICourse):
        """
        Open edit profile page in browser
        Args:
            user: The user to edit
            course: The course context
        """
        if user and course and user.id and course.id:
            url = f"{course.lms.host}{EDIT_PROFILE_IN_COURSE % (user.id, course.id)}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_create_user_in_browser(lms: ILMS):
        """
        Open create user page in browser
        Args:
            lms: The LMS instance
        """
        if lms and lms.host:
            url = f"{lms.host}{USER_CREATE}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_edit_course_in_browser(course: ICourse):
        """
        Open edit course page in browser
        Args:
            course: The course to edit
        """
        if course and course.lms and course.id:
            url = f"{course.lms.host}{EDIT_COURSE % course.id}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_external_services(lms: ILMS):
        """
        Open external services page in browser
        Args:
            lms: The LMS instance
        """
        if lms and lms.host:
            url = f"{lms.host}{ADMIN_SETTINGS_EXTERNALSERVICES}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_web_service_documentation(lms: ILMS):
        """
        Open web service documentation page in browser
        Args:
            lms: The LMS instance
        """
        if lms and lms.host:
            url = f"{lms.host}{ADMIN_WEBSERVICE_DOCUMENTATION}"
            BrowserHelper.open_in_browser(url)
    
    @staticmethod
    def open_shell(path: str):
        """
        Open path in system file explorer
        Args:
            path: The path to open
        """
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open '{path}'")
            else:  # Linux
                os.system(f"xdg-open '{path}'")
        except Exception as e:
            print(f"Failed to open path {path}: {e}")


# Backward compatibility functions
def OpenInBrowser(url: str):
    """Open URL in browser (backward compatibility)"""
    BrowserHelper.open_in_browser(url)


def OpenInBrowserLMS(lms: ILMS):
    """Open LMS in browser (backward compatibility)"""
    BrowserHelper.open_lms_in_browser(lms)


def OpenInBrowserCategory(category: ICategory):
    """Open category in browser (backward compatibility)"""
    BrowserHelper.open_category_in_browser(category)


def OpenInBrowserCourse(course: ICourse):
    """Open course in browser (backward compatibility)"""
    BrowserHelper.open_course_in_browser(course)


def OpenInBrowserUser(user: IUser):
    """Open user in browser (backward compatibility)"""
    BrowserHelper.open_user_in_browser(user)


def OpenUsersInBrowserLMS(lms: ILMS):
    """Open users page for LMS (backward compatibility)"""
    BrowserHelper.open_users_in_browser_lms(lms)


def OpenUsersInBrowserCourse(course: ICourse):
    """Open users page for course (backward compatibility)"""
    BrowserHelper.open_users_in_browser_course(course)


def OpenUploadUsersInBrowser(lms: ILMS):
    """Open upload users page (backward compatibility)"""
    BrowserHelper.open_upload_users_in_browser(lms)


def OpenEditCourseInBrowser(course: ICourse):
    """Open edit course page (backward compatibility)"""
    BrowserHelper.open_edit_course_in_browser(course)
