"""
Course Form
Form for displaying course information, content, and users
"""

from typing import Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QToolBar, QAction, QTabWidget, QStatusBar, QLabel,
                             QLineEdit, QApplication, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import ICourse, IUser
from tree_views.course_content_tree import CourseContentTreeWidget
from tree_views.course_users_tree import CourseUsersTreeWidget
from helpers.browser import BrowserHelper
from helpers.reports import ReportsHelper
from helpers.logger import LogHelper


class CourseForm(QMainWindow):
    """Form for displaying course information, content, and users"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.course: Optional[ICourse] = None
        self.filter_user: Optional[IUser] = None
        self.course_content_tree: Optional[CourseContentTreeWidget] = None
        self.course_users_tree: Optional[CourseUsersTreeWidget] = None
        
        self.setup_ui()
        self.setup_actions()
        
    def setup_ui(self):
        """Setup the form UI"""
        self.setWindowTitle("Course")
        self.resize(1000, 700)
        
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
        
        # Create users tab
        users_widget = QWidget()
        users_layout = QVBoxLayout(users_widget)
        
        # Filter edit
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Enter filter text...")
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)
        users_layout.addLayout(filter_layout)
        
        # Course users tree view
        self.course_users_tree = CourseUsersTreeWidget()
        users_layout.addWidget(self.course_users_tree)
        
        # Add users tab
        self.tab_widget.addTab(users_widget, "Users")
        
        # Create content tab
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Content toolbar
        self.content_toolbar = QToolBar()
        content_layout.addWidget(self.content_toolbar)
        
        # Course content tree view
        self.course_content_tree = CourseContentTreeWidget()
        content_layout.addWidget(self.course_content_tree)
        
        # Add content tab
        self.tab_widget.addTab(content_widget, "Content")
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Connect signals
        self.filter_edit.textChanged.connect(self.on_filter_changed)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.course_users_tree.user_double_clicked.connect(self.on_user_double_clicked)
        self.course_content_tree.content_double_clicked.connect(self.on_content_double_clicked)
        
    def setup_actions(self):
        """Setup toolbar actions"""
        # Open course action
        self.open_course_action = QAction("Open Course", self)
        self.open_course_action.setStatusTip("Open course in browser")
        self.open_course_action.triggered.connect(self.open_course)
        self.toolbar.addAction(self.open_course_action)
        
        # Open users action
        self.open_users_action = QAction("Open Users", self)
        self.open_users_action.setStatusTip("Open course users in browser")
        self.open_users_action.triggered.connect(self.open_users)
        self.toolbar.addAction(self.open_users_action)
        
        # Separator
        self.toolbar.addSeparator()
        
        # Export action
        self.export_action = QAction("Export to Excel", self)
        self.export_action.setStatusTip("Export course data to Excel")
        self.export_action.triggered.connect(self.export_to_excel)
        self.toolbar.addAction(self.export_action)
        
        # Refresh action
        self.refresh_action = QAction("Refresh", self)
        self.refresh_action.setStatusTip("Refresh course data")
        self.refresh_action.triggered.connect(self.refresh)
        self.toolbar.addAction(self.refresh_action)
        
        # Content toolbar actions
        self.download_content_action = QAction("Download All Content", self)
        self.download_content_action.setStatusTip("Download all course content")
        self.download_content_action.triggered.connect(self.download_all_content)
        self.content_toolbar.addAction(self.download_content_action)
        
        self.show_resources_action = QAction("Show Resources Only", self)
        self.show_resources_action.setStatusTip("Show only resource modules")
        self.show_resources_action.triggered.connect(self.show_resources_only)
        self.content_toolbar.addAction(self.show_resources_action)
        
    def set_course(self, course: ICourse):
        """Set the course and update the form"""
        self.course = course
        
        if course:
            self.setWindowTitle(f"Course: {course.fullname}")
            self.course_users_tree.set_course(course)
            self.course_content_tree.set_course(course)
            self.update_action_states()
        else:
            self.setWindowTitle("Course")
            self.course_users_tree.clear_course()
            self.course_content_tree.clear_course()
            
    def set_filter_user(self, user: IUser):
        """Set the filter user"""
        self.filter_user = user
        # Apply filter logic here if needed
        
    def update_action_states(self):
        """Update action enabled states"""
        enabled = self.course is not None
        self.open_course_action.setEnabled(enabled)
        self.open_users_action.setEnabled(enabled)
        self.export_action.setEnabled(enabled)
        self.refresh_action.setEnabled(enabled)
        self.download_content_action.setEnabled(enabled)
        self.show_resources_action.setEnabled(enabled)
        
    def open_course(self):
        """Open course in browser"""
        if self.course:
            BrowserHelper.open_course(self.course)
            
    def open_users(self):
        """Open course users in browser"""
        if self.course:
            BrowserHelper.open_course_users(self.course)
            
    def export_to_excel(self):
        """Export course data to Excel"""
        if self.course:
            try:
                ReportsHelper.export_to_excel(self.course)
                self.status_bar.showMessage("Export completed successfully", 3000)
            except Exception as e:
                LogHelper.log_error(f"Export failed: {str(e)}")
                self.status_bar.showMessage("Export failed", 3000)
                
    def refresh(self):
        """Refresh the course data"""
        if self.course:
            self.course_users_tree.refresh()
            self.course_content_tree.refresh()
            
    def download_all_content(self):
        """Download all course content"""
        if self.course and self.course.lms:
            try:
                self.course.lms.download_all_course_content(self.course)
                self.status_bar.showMessage("Download started", 3000)
            except Exception as e:
                LogHelper.log_error(f"Download failed: {str(e)}")
                self.status_bar.showMessage("Download failed", 3000)
                
    def show_resources_only(self):
        """Show only resource modules"""
        if self.course_content_tree:
            self.course_content_tree.show_only_resources()
            
    def on_filter_changed(self, text):
        """Handle filter text change"""
        if self.course_users_tree:
            self.course_users_tree.filter_by_text(text)
            
    def on_tab_changed(self, index):
        """Handle tab change"""
        # Update UI based on selected tab
        pass
        
    def on_user_double_clicked(self, user):
        """Handle user double click"""
        # This would typically open a user form
        pass
        
    def on_content_double_clicked(self, content):
        """Handle content double click"""
        # This would typically open the content
        if content and content.file_url:
            BrowserHelper.open_url(content.file_url)
            
    def closeEvent(self, event):
        """Handle form close event"""
        # Clean up resources
        if self.course_users_tree:
            self.course_users_tree.clear_course()
        if self.course_content_tree:
            self.course_content_tree.clear_course()
        super().closeEvent(event)
