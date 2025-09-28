"""
Category Form
Form for displaying category information and courses
"""

from typing import Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QToolBar, QAction, QTabWidget, QStatusBar, QLabel,
                             QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import ICategory
from tree_views.course_category_tree import CourseCategoryTreeWidget
from helpers.browser import BrowserHelper


class CategoryForm(QMainWindow):
    """Form for displaying category information and courses"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.category: Optional[ICategory] = None
        self.category_tree_view: Optional[CourseCategoryTreeWidget] = None
        
        self.setup_ui()
        self.setup_actions()
        
    def setup_ui(self):
        """Setup the form UI"""
        self.setWindowTitle("Category")
        self.resize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create category tree view
        self.category_tree_view = CourseCategoryTreeWidget()
        self.tab_widget.addTab(self.category_tree_view, "Courses")
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connect signals
        self.category_tree_view.course_double_clicked.connect(self.on_course_double_clicked)
        
    def setup_actions(self):
        """Setup toolbar actions"""
        # Open all courses action
        self.open_all_courses_action = QAction("Open All Courses", self)
        self.open_all_courses_action.setStatusTip("Open all courses in this category in browser")
        self.open_all_courses_action.triggered.connect(self.open_all_courses)
        self.toolbar.addAction(self.open_all_courses_action)
        
        # Open all users action
        self.open_all_users_action = QAction("Open All Users", self)
        self.open_all_users_action.setStatusTip("Open all users in this category in browser")
        self.open_all_users_action.triggered.connect(self.open_all_users)
        self.toolbar.addAction(self.open_all_users_action)
        
        # Separator
        self.toolbar.addSeparator()
        
        # Refresh action
        self.refresh_action = QAction("Refresh", self)
        self.refresh_action.setStatusTip("Refresh category data")
        self.refresh_action.triggered.connect(self.refresh)
        self.toolbar.addAction(self.refresh_action)
        
    def set_category(self, category: ICategory):
        """Set the category and update the form"""
        self.category = category
        
        if category:
            self.setWindowTitle(f"Category: {category.name}")
            self.category_tree_view.set_category(category)
            self.update_action_states()
        else:
            self.setWindowTitle("Category")
            self.category_tree_view.clear_category()
            
    def update_action_states(self):
        """Update action enabled states"""
        if self.category:
            # Enable actions only if category has no subcategories
            has_subcategories = self.category.sub_categories_count > 0
            self.open_all_courses_action.setEnabled(not has_subcategories)
            self.open_all_users_action.setEnabled(not has_subcategories)
        else:
            self.open_all_courses_action.setEnabled(False)
            self.open_all_users_action.setEnabled(False)
            
    def open_all_courses(self):
        """Open all courses in browser"""
        if self.category:
            for course in self.category.courses:
                BrowserHelper.open_course(course)
                
    def open_all_users(self):
        """Open all users in browser"""
        if self.category:
            for course in self.category.courses:
                BrowserHelper.open_course_users(course)
                
    def refresh(self):
        """Refresh the category data"""
        if self.category:
            self.category_tree_view.refresh()
            
    def on_course_double_clicked(self, course):
        """Handle course double click"""
        # This would typically open a course form
        pass
        
    def closeEvent(self, event):
        """Handle form close event"""
        # Clean up resources
        if self.category_tree_view:
            self.category_tree_view.clear_category()
        super().closeEvent(event)
