"""
Form Factory helper for LMS Explorer
Handles creation and display of forms/dialogs
"""

from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QWidget, QMainWindow
from lms_interface import ILMS, ICourse, ICategory, IUser


class FormFactory:
    """Factory class for creating and managing forms"""
    
    def __init__(self, main_window: Optional[QMainWindow] = None):
        self.main_window = main_window
        self._form_cache: Dict[str, QWidget] = {}
        
        # Import form classes here to avoid circular imports
        self._import_form_classes()
    
    def _import_form_classes(self):
        """Import form classes dynamically"""
        try:
            from dialogs.course_dialog import CourseDialog
            from dialogs.category_dialog import CategoryDialog
            from dialogs.user_dialog import UserDialog
            from dialogs.lms_dialog import LMSDialog
            
            self.CourseDialog = CourseDialog
            self.CategoryDialog = CategoryDialog
            self.UserDialog = UserDialog
            self.LMSDialog = LMSDialog
            
        except ImportError as e:
            print(f"Warning: Could not import form classes: {e}")
            # Set placeholder classes
            self.CourseDialog = None
            self.CategoryDialog = None
            self.UserDialog = None
            self.LMSDialog = None
    
    def view_course_form(self, course: ICourse, user: Optional[IUser] = None):
        """
        Create and show course form
        Args:
            course: The course to view/edit
            user: Optional user to filter/select
        """
        if not self.CourseDialog:
            print("CourseDialog not available")
            return
        
        try:
            # Create course dialog
            if self.main_window:
                dialog = self.CourseDialog(course, parent=self.main_window)
            else:
                dialog = self.CourseDialog(course)
            
            # Set filter user if provided
            if user:
                dialog.set_filter_user(user)
            
            dialog.show()
            
        except Exception as e:
            print(f"Error creating course form: {e}")
    
    def view_category_form(self, category: ICategory):
        """
        Create and show category form
        Args:
            category: The category to view/edit
        """
        if not self.CategoryDialog:
            print("CategoryDialog not available")
            return
        
        try:
            # Create category dialog
            if self.main_window:
                dialog = self.CategoryDialog(category, parent=self.main_window)
            else:
                dialog = self.CategoryDialog(category)
            
            dialog.show()
            
        except Exception as e:
            print(f"Error creating category form: {e}")
    
    def view_user_form(self, user: IUser):
        """
        Create and show user form
        Args:
            user: The user to view/edit
        """
        if not self.UserDialog:
            print("UserDialog not available")
            return
        
        try:
            # Create user dialog
            if self.main_window:
                dialog = self.UserDialog(user, parent=self.main_window)
            else:
                dialog = self.UserDialog(user)
            
            dialog.show()
            
        except Exception as e:
            print(f"Error creating user form: {e}")
    
    def view_lms_form(self, lms: ILMS):
        """
        Create and show LMS form
        Args:
            lms: The LMS to view/edit
        """
        if not self.LMSDialog:
            print("LMSDialog not available")
            return
        
        try:
            # Create LMS dialog
            if self.main_window:
                dialog = self.LMSDialog(lms, parent=self.main_window)
            else:
                dialog = self.LMSDialog(lms)
            
            dialog.show()
            
        except Exception as e:
            print(f"Error creating LMS form: {e}")
    
    def create_course_dialog(self, course: ICourse, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """
        Create course dialog without showing it
        Args:
            course: The course for the dialog
            parent: Parent widget
        Returns:
            Created dialog or None if failed
        """
        if not self.CourseDialog:
            return None
        
        try:
            if parent:
                return self.CourseDialog(course, parent=parent)
            else:
                return self.CourseDialog(course)
        except Exception as e:
            print(f"Error creating course dialog: {e}")
            return None
    
    def create_category_dialog(self, category: ICategory, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """
        Create category dialog without showing it
        Args:
            category: The category for the dialog
            parent: Parent widget
        Returns:
            Created dialog or None if failed
        """
        if not self.CategoryDialog:
            return None
        
        try:
            if parent:
                return self.CategoryDialog(category, parent=parent)
            else:
                return self.CategoryDialog(category)
        except Exception as e:
            print(f"Error creating category dialog: {e}")
            return None
    
    def create_user_dialog(self, user: IUser, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """
        Create user dialog without showing it
        Args:
            user: The user for the dialog
            parent: Parent widget
        Returns:
            Created dialog or None if failed
        """
        if not self.UserDialog:
            return None
        
        try:
            if parent:
                return self.UserDialog(user, parent=parent)
            else:
                return self.UserDialog(user)
        except Exception as e:
            print(f"Error creating user dialog: {e}")
            return None
    
    def create_lms_dialog(self, lms: ILMS, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """
        Create LMS dialog without showing it
        Args:
            lms: The LMS for the dialog
            parent: Parent widget
        Returns:
            Created dialog or None if failed
        """
        if not self.LMSDialog:
            return None
        
        try:
            if parent:
                return self.LMSDialog(lms, parent=parent)
            else:
                return self.LMSDialog(lms)
        except Exception as e:
            print(f"Error creating LMS dialog: {e}")
            return None
    
    def cache_form(self, key: str, form: QWidget):
        """
        Cache a form for later use
        Args:
            key: Cache key
            form: Form widget to cache
        """
        self._form_cache[key] = form
    
    def get_cached_form(self, key: str) -> Optional[QWidget]:
        """
        Get a cached form
        Args:
            key: Cache key
        Returns:
            Cached form or None if not found
        """
        return self._form_cache.get(key)
    
    def clear_cache(self):
        """Clear all cached forms"""
        for form in self._form_cache.values():
            if form:
                form.close()
                form.deleteLater()
        self._form_cache.clear()
    
    def set_main_window(self, main_window: QMainWindow):
        """
        Set the main window reference
        Args:
            main_window: Main application window
        """
        self.main_window = main_window


# Global form factory instance
_global_form_factory: Optional[FormFactory] = None


def get_form_factory(main_window: Optional[QMainWindow] = None) -> FormFactory:
    """Get the global form factory instance"""
    global _global_form_factory
    if _global_form_factory is None:
        _global_form_factory = FormFactory(main_window)
    elif main_window:
        _global_form_factory.set_main_window(main_window)
    return _global_form_factory


def set_main_window(main_window: QMainWindow):
    """Set the main window for the global form factory"""
    get_form_factory(main_window)


# Backward compatibility functions
def ViewFormCourse(course: ICourse):
    """View course form (backward compatibility)"""
    get_form_factory().view_course_form(course)


def ViewFormCourseUser(course: ICourse, user: IUser):
    """View course form with user (backward compatibility)"""
    get_form_factory().view_course_form(course, user)


def ViewFormCategory(category: ICategory):
    """View category form (backward compatibility)"""
    get_form_factory().view_category_form(category)


def ViewFormUser(user: IUser):
    """View user form (backward compatibility)"""
    get_form_factory().view_user_form(user)


def ViewFormLMS(lms: ILMS):
    """View LMS form (backward compatibility)"""
    get_form_factory().view_lms_form(lms)
