"""
User Form
Form for displaying user information and details
"""

from typing import Optional
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QGroupBox,
                             QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import IUser, ICourse
from helpers.browser import BrowserHelper


class UserForm(QDialog):
    """Form for displaying user information and details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.user: Optional[IUser] = None
        self.course: Optional[ICourse] = None
        
        self.setup_ui()
        self.setup_actions()
        
    def setup_ui(self):
        """Setup the form UI"""
        self.setWindowTitle("User Information")
        self.resize(600, 500)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create info tab
        self.create_info_tab()
        
        # Create courses tab
        self.create_courses_tab()
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Add buttons
        self.open_profile_button = QPushButton("Open Profile")
        self.open_profile_button.clicked.connect(self.open_user_profile)
        button_layout.addWidget(self.open_profile_button)
        
        self.open_grades_button = QPushButton("View Grades")
        self.open_grades_button.clicked.connect(self.view_user_grades)
        button_layout.addWidget(self.open_grades_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
        
    def create_info_tab(self):
        """Create the user information tab"""
        info_widget = QWidget()
        info_layout = QFormLayout(info_widget)
        
        # Basic information group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.id_label = QLabel()
        basic_layout.addRow("ID:", self.id_label)
        
        self.username_edit = QLineEdit()
        self.username_edit.setReadOnly(True)
        basic_layout.addRow("Username:", self.username_edit)
        
        self.firstname_edit = QLineEdit()
        self.firstname_edit.setReadOnly(True)
        basic_layout.addRow("First Name:", self.firstname_edit)
        
        self.lastname_edit = QLineEdit()
        self.lastname_edit.setReadOnly(True)
        basic_layout.addRow("Last Name:", self.lastname_edit)
        
        self.fullname_edit = QLineEdit()
        self.fullname_edit.setReadOnly(True)
        basic_layout.addRow("Full Name:", self.fullname_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setReadOnly(True)
        basic_layout.addRow("Email:", self.email_edit)
        
        info_layout.addWidget(basic_group)
        
        # Additional information group
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout(additional_group)
        
        self.roles_edit = QLineEdit()
        self.roles_edit.setReadOnly(True)
        additional_layout.addRow("Roles:", self.roles_edit)
        
        self.last_access_edit = QLineEdit()
        self.last_access_edit.setReadOnly(True)
        additional_layout.addRow("Last Access:", self.last_access_edit)
        
        self.last_access_from_edit = QLineEdit()
        self.last_access_from_edit.setReadOnly(True)
        additional_layout.addRow("Last Access From:", self.last_access_from_edit)
        
        self.time_created_edit = QLineEdit()
        self.time_created_edit.setReadOnly(True)
        additional_layout.addRow("Time Created:", self.time_created_edit)
        
        self.time_modified_edit = QLineEdit()
        self.time_modified_edit.setReadOnly(True)
        additional_layout.addRow("Time Modified:", self.time_modified_edit)
        
        info_layout.addWidget(additional_group)
        
        # Notes group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setReadOnly(True)
        notes_layout.addWidget(self.notes_edit)
        
        info_layout.addWidget(notes_group)
        
        self.tab_widget.addTab(info_widget, "Information")
        
    def create_courses_tab(self):
        """Create the user courses tab"""
        courses_widget = QWidget()
        courses_layout = QVBoxLayout(courses_widget)
        
        # Courses table
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(4)
        self.courses_table.setHorizontalHeaderLabels(["Course", "Role", "Last Access", "Status"])
        
        # Set table properties
        header = self.courses_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.courses_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.courses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.courses_table.setAlternatingRowColors(True)
        
        courses_layout.addWidget(self.courses_table)
        
        self.tab_widget.addTab(courses_widget, "Courses")
        
    def setup_actions(self):
        """Setup actions and signals"""
        # Connect table double click
        self.courses_table.doubleClicked.connect(self.on_course_double_clicked)
        
    def set_user(self, user: IUser, course: Optional[ICourse] = None):
        """Set the user and update the form"""
        self.user = user
        self.course = course
        
        if user:
            self.setWindowTitle(f"User: {user.full_name or user.username}")
            self.update_user_info()
            self.update_courses_table()
            self.update_button_states()
        else:
            self.setWindowTitle("User Information")
            self.clear_form()
            
    def update_user_info(self):
        """Update user information fields"""
        if not self.user:
            return
            
        self.id_label.setText(str(self.user.id))
        self.username_edit.setText(self.user.username or "")
        self.firstname_edit.setText(self.user.first_name or "")
        self.lastname_edit.setText(self.user.last_name or "")
        self.fullname_edit.setText(self.user.full_name or "")
        self.email_edit.setText(self.user.email or "")
        self.roles_edit.setText(self.user.roles or "")
        self.last_access_edit.setText(self.user.last_access or "")
        self.last_access_from_edit.setText(self.user.last_access_from or "")
        self.time_created_edit.setText(self.user.time_created or "")
        self.time_modified_edit.setText(self.user.time_modified or "")
        self.notes_edit.setText(self.user.notes or "")
        
    def update_courses_table(self):
        """Update the courses table"""
        self.courses_table.setRowCount(0)
        
        if not self.user:
            return
            
        # This would typically load user's courses from the LMS
        # For now, we'll show a placeholder
        # In a real implementation, you would get the user's enrolled courses
        pass
        
    def update_button_states(self):
        """Update button enabled states"""
        enabled = self.user is not None
        self.open_profile_button.setEnabled(enabled)
        self.open_grades_button.setEnabled(enabled)
        
    def open_user_profile(self):
        """Open user profile in browser"""
        if self.user and self.course:
            BrowserHelper.open_user_profile(self.course, self.user)
        elif self.user:
            # Try to find a course for this user
            # This would typically be handled by the parent form
            pass
            
    def view_user_grades(self):
        """View user grades"""
        if self.user and self.course:
            # This would typically open a grades dialog
            pass
            
    def on_course_double_clicked(self, index):
        """Handle course double click"""
        # This would typically open a course form
        pass
        
    def clear_form(self):
        """Clear all form fields"""
        self.id_label.setText("")
        self.username_edit.setText("")
        self.firstname_edit.setText("")
        self.lastname_edit.setText("")
        self.fullname_edit.setText("")
        self.email_edit.setText("")
        self.roles_edit.setText("")
        self.last_access_edit.setText("")
        self.last_access_from_edit.setText("")
        self.time_created_edit.setText("")
        self.time_modified_edit.setText("")
        self.notes_edit.setText("")
        self.courses_table.setRowCount(0)
        
    def closeEvent(self, event):
        """Handle form close event"""
        # Clean up resources
        self.clear_form()
        super().closeEvent(event)
