"""
User Profile Dialog for Moodle Manager
Provides comprehensive user profile viewing and editing functionality
"""

import os
import sys


# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QCheckBox, QGroupBox, QProgressBar, 
                             QMessageBox, QFrame, QSpacerItem, QSizePolicy, QTextEdit,
                             QTabWidget, QWidget, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QComboBox, QSpinBox, QFormLayout, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, QDate
from PyQt5.QtGui import QIcon, QFont, QPalette, QPixmap
import sys
import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from core.data_models import IUser
from services.moodle.moodle_rest import MoodleRestClient

logger = logging.getLogger(__name__)


class UserProfileDialog(QDialog):
    """Comprehensive user profile dialog"""
    
    profile_updated = pyqtSignal(dict)  # Emits updated user data
    profile_picture_updated = pyqtSignal(str)  # Emits new picture path
    
    def __init__(self, user: IUser, parent=None, moodle_client: MoodleRestClient = None):
        super().__init__(parent)
        self.user = user
        self.moodle_client = moodle_client
        self.original_data = {}
        self.setup_ui()
        self.load_user_data()
        
    def setup_ui(self):
        """Setup the user profile dialog UI"""
        self.setWindowTitle(f"User Profile - {self.user.get_full_name()}")
        self.setModal(True)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with user info
        header_layout = QHBoxLayout()
        
        # Profile picture placeholder
        self.profile_picture_label = QLabel()
        self.profile_picture_label.setFixedSize(120, 120)
        self.profile_picture_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 60px;
                background-color: #f5f5f5;
                color: #666;
                font-size: 12px;
            }
        """)
        self.profile_picture_label.setAlignment(Qt.AlignCenter)
        self.profile_picture_label.setText("No Picture")
        header_layout.addWidget(self.profile_picture_label)
        
        # User name and title
        info_layout = QVBoxLayout()
        self.name_label = QLabel()
        name_font = QFont()
        name_font.setPointSize(18)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        info_layout.addWidget(self.name_label)
        
        self.email_label = QLabel()
        email_font = QFont()
        email_font.setPointSize(12)
        self.email_label.setFont(email_font)
        self.email_label.setStyleSheet("color: #666;")
        info_layout.addWidget(self.email_label)
        
        self.roles_label = QLabel()
        info_layout.addWidget(self.roles_label)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        
        header_layout.addStretch()
        
        # Upload picture button
        self.upload_picture_btn = QPushButton("📷 Upload Picture")
        self.upload_picture_btn.clicked.connect(self.upload_profile_picture)
        header_layout.addWidget(self.upload_picture_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        
        # Basic Info Tab
        self.basic_info_tab = self.create_basic_info_tab()
        self.tab_widget.addTab(self.basic_info_tab, "📝 Basic Info")
        
        # Academic Info Tab
        self.academic_info_tab = self.create_academic_info_tab()
        self.tab_widget.addTab(self.academic_info_tab, "🎓 Academic Info")
        
        # Courses Tab
        self.courses_tab = self.create_courses_tab()
        self.tab_widget.addTab(self.courses_tab, "📚 Courses")
        
        # Activity Tab
        self.activity_tab = self.create_activity_tab()
        self.tab_widget.addTab(self.activity_tab, "📊 Activity")
        
        main_layout.addWidget(self.tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("💾 Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.save_button)
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_button)
        
        self.close_button = QPushButton("❌ Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def create_basic_info_tab(self) -> QWidget:
        """Create basic information tab"""
        widget = QWidget()
        layout = QFormLayout()
        
        # Personal Information
        personal_group = QGroupBox("Personal Information")
        personal_layout = QFormLayout()
        
        self.first_name_edit = QLineEdit()
        personal_layout.addRow("First Name:", self.first_name_edit)
        
        self.last_name_edit = QLineEdit()
        personal_layout.addRow("Last Name:", self.last_name_edit)
        
        self.email_edit = QLineEdit()
        personal_layout.addRow("Email:", self.email_edit)
        
        self.username_edit = QLineEdit()
        self.username_edit.setReadOnly(True)
        personal_layout.addRow("Username:", self.username_edit)
        
        self.id_edit = QLineEdit()
        self.id_edit.setReadOnly(True)
        personal_layout.addRow("User ID:", self.id_edit)
        
        personal_group.setLayout(personal_layout)
        layout.addRow(personal_group)
        
        # Contact Information
        contact_group = QGroupBox("Contact Information")
        contact_layout = QFormLayout()
        
        self.phone_edit = QLineEdit()
        contact_layout.addRow("Phone:", self.phone_edit)
        
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(80)
        contact_layout.addRow("Address:", self.address_edit)
        
        self.city_edit = QLineEdit()
        contact_layout.addRow("City:", self.city_edit)
        
        self.country_edit = QLineEdit()
        contact_layout.addRow("Country:", self.country_edit)
        
        contact_group.setLayout(contact_layout)
        layout.addRow(contact_group)
        
        # Additional Information
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout()
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        additional_layout.addRow("Description:", self.description_edit)
        
        self.interests_edit = QLineEdit()
        additional_layout.addRow("Interests:", self.interests_edit)
        
        additional_group.setLayout(additional_layout)
        layout.addRow(additional_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_academic_info_tab(self) -> QWidget:
        """Create academic information tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Academic Details
        academic_group = QGroupBox("Academic Details")
        academic_layout = QFormLayout()
        
        self.institution_edit = QLineEdit()
        academic_layout.addRow("Institution:", self.institution_edit)
        
        self.department_edit = QLineEdit()
        academic_layout.addRow("Department:", self.department_edit)
        
        self.id_number_edit = QLineEdit()
        academic_layout.addRow("ID Number:", self.id_number_edit)
        
        academic_group.setLayout(academic_layout)
        layout.addWidget(academic_group)
        
        # Moodle-specific info
        moodle_group = QGroupBox("Moodle Information")
        moodle_layout = QFormLayout()
        
        self.last_access_label = QLabel()
        moodle_layout.addRow("Last Access:", self.last_access_label)
        
        self.time_created_label = QLabel()
        moodle_layout.addRow("Account Created:", self.time_created_label)
        
        self.auth_method_edit = QComboBox()
        self.auth_method_edit.addItems(["manual", "ldap", "oauth2", "shibboleth", "webservice"])
        moodle_layout.addRow("Authentication Method:", self.auth_method_edit)
        
        self.timezone_edit = QComboBox()
        self.timezone_edit.addItems(["UTC", "Europe/London", "America/New_York", "Asia/Tokyo"])
        moodle_layout.addRow("Timezone:", self.timezone_edit)
        
        self.lang_edit = QComboBox()
        self.lang_edit.addItems(["en", "es", "fr", "de", "it", "pt", "zh"])
        moodle_layout.addRow("Language:", self.lang_edit)
        
        moodle_group.setLayout(moodle_layout)
        layout.addWidget(moodle_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_courses_tab(self) -> QWidget:
        """Create courses information tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Enrolled Courses Table
        courses_group = QGroupBox("Enrolled Courses")
        courses_layout = QVBoxLayout()
        
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(5)
        self.courses_table.setHorizontalHeaderLabels(["Course Name", "Category", "Role", "Enrolled", "Last Access"])
        self.courses_table.horizontalHeader().setStretchLastSection(True)
        self.courses_table.setAlternatingRowColors(True)
        self.courses_table.setSelectionBehavior(QTableWidget.SelectRows)
        courses_layout.addWidget(self.courses_table)
        
        courses_group.setLayout(courses_layout)
        layout.addWidget(courses_group)
        
        widget.setLayout(layout)
        return widget
        
    def create_activity_tab(self) -> QWidget:
        """Create activity information tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Recent Activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Activity", "Course", "Date", "Status"])
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectRows)
        activity_layout.addWidget(self.activity_table)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout()
        
        self.total_courses_label = QLabel("0")
        stats_layout.addRow("Total Courses:", self.total_courses_label)
        
        self.completed_courses_label = QLabel("0")
        stats_layout.addRow("Completed Courses:", self.completed_courses_label)
        
        self.total_activities_label = QLabel("0")
        stats_layout.addRow("Total Activities:", self.total_activities_label)
        
        self.last_login_label = QLabel("Never")
        stats_layout.addRow("Last Login:", self.last_login_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def load_user_data(self):
        """Load user data into form fields"""
        try:
            # Store original data for comparison
            self.original_data = {
                'firstname': self.user.get_first_name(),
                'lastname': self.user.get_last_name(),
                'email': self.user.get_email(),
                'username': getattr(self.user, '_username', ''),
                'id': self.user.get_id()
            }
            
            # Basic info
            self.name_label.setText(self.user.get_full_name())
            self.email_label.setText(self.user.get_email())
            self.username_edit.setText(getattr(self.user, '_username', ''))
            self.id_edit.setText(str(self.user.get_id()))
            
            self.first_name_edit.setText(self.user.get_first_name())
            self.last_name_edit.setText(self.user.get_last_name())
            self.email_edit.setText(self.user.get_email())
            
            # Roles
            roles = self.user.get_roles()
            if roles:
                self.roles_label.setText(f"Roles: {', '.join(roles)}")
            else:
                self.roles_label.setText("Roles: Student")
            
            # Load additional data if Moodle client is available
            if self.moodle_client:
                self.load_extended_user_data()
                
            logger.info(f"Loaded profile data for user: {self.user.get_full_name()}")
            
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
            QMessageBox.warning(self, "Load Error", f"Failed to load user data: {str(e)}")
            
    def load_extended_user_data(self):
        """Load extended user data from Moodle"""
        try:
            if not self.moodle_client:
                return
                
            # Get user by field for more detailed information
            user_data = self.moodle_client.get_user_by_field('id', str(self.user.get_id()))
            
            if user_data:
                # Update fields with Moodle data
                self.phone_edit.setText(user_data.get('phone1', ''))
                self.address_edit.setPlainText(user_data.get('address', ''))
                self.city_edit.setText(user_data.get('city', ''))
                self.country_edit.setText(user_data.get('country', ''))
                self.description_edit.setPlainText(user_data.get('description', ''))
                self.interests_edit.setText(user_data.get('interests', ''))
                self.institution_edit.setText(user_data.get('institution', ''))
                self.department_edit.setText(user_data.get('department', ''))
                self.id_number_edit.setText(user_data.get('idnumber', ''))
                
                # Moodle-specific fields
                self.last_access_label.setText(user_data.get('lastaccess', 'Never'))
                self.time_created_label.setText(user_data.get('timecreated', 'Unknown'))
                
                # Set auth method
                auth_method = user_data.get('auth', 'manual')
                index = self.auth_method_edit.findText(auth_method)
                if index >= 0:
                    self.auth_method_edit.setCurrentIndex(index)
                    
                # Set timezone
                timezone = user_data.get('timezone', 'UTC')
                index = self.timezone_edit.findText(timezone)
                if index >= 0:
                    self.timezone_edit.setCurrentIndex(index)
                    
                # Set language
                lang = user_data.get('lang', 'en')
                index = self.lang_edit.findText(lang)
                if index >= 0:
                    self.lang_edit.setCurrentIndex(index)
                
                # Load profile picture if available
                self.load_profile_picture()
                
            # Load enrolled courses
            self.load_enrolled_courses()
            
        except Exception as e:
            logger.error(f"Error loading extended user data: {e}")
            
    def load_profile_picture(self):
        """Load user profile picture"""
        try:
            if not self.moodle_client:
                return
                
            # Get user profile picture URL
            user_data = self.moodle_client.get_user_by_field('id', str(self.user.get_id()))
            if user_data and 'profileimageurl' in user_data:
                picture_url = user_data['profileimageurl']
                
                # Download and display picture
                response = requests.get(picture_url)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    
                    # Scale and crop to circular shape
                    scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    
                    # Create circular mask
                    mask = QPixmap(120, 120)
                    mask.fill(Qt.transparent)
                    
                    # Apply circular mask (simplified version)
                    self.profile_picture_label.setPixmap(scaled_pixmap)
                    self.profile_picture_label.setStyleSheet("""
                        QLabel {
                            border: 2px solid #4CAF50;
                            border-radius: 60px;
                            background-color: white;
                        }
                    """)
                    
        except Exception as e:
            logger.error(f"Error loading profile picture: {e}")
            
    def load_enrolled_courses(self):
        """Load user's enrolled courses"""
        try:
            if not self.moodle_client:
                return
                
            # Get user's courses
            courses_data = self.moodle_client.get_users_courses(self.user.get_id())
            
            if courses_data:
                self.courses_table.setRowCount(len(courses_data))
                
                for row, course in enumerate(courses_data):
                    self.courses_table.setItem(row, 0, QTableWidgetItem(course.get('fullname', 'Unknown')))
                    self.courses_table.setItem(row, 1, QTableWidgetItem(course.get('category', 'Unknown')))
                    self.courses_table.setItem(row, 2, QTableWidgetItem(course.get('shortname', 'Student')))
                    self.courses_table.setItem(row, 3, QTableWidgetItem(course.get('timeaccess', 'Unknown')))
                    self.courses_table.setItem(row, 4, QTableWidgetItem(course.get('lastaccess', 'Never')))
                    
                # Update statistics
                self.total_courses_label.setText(str(len(courses_data)))
                
        except Exception as e:
            logger.error(f"Error loading enrolled courses: {e}")
            
    def upload_profile_picture(self):
        """Handle profile picture upload"""
        QMessageBox.information(self, "Upload Picture", 
                               "Profile picture upload would open file dialog here.\n"
                               "This feature requires implementation of file upload functionality.")
        
    def save_changes(self):
        """Save changes to user profile"""
        try:
            if not self.moodle_client:
                QMessageBox.warning(self, "No Connection", "Not connected to Moodle. Changes cannot be saved.")
                return
                
            # Collect updated data
            updated_data = {
                'id': self.user.get_id(),
                'firstname': self.first_name_edit.text().strip(),
                'lastname': self.last_name_edit.text().strip(),
                'email': self.email_edit.text().strip(),
                'phone1': self.phone_edit.text().strip(),
                'address': self.address_edit.toPlainText().strip(),
                'city': self.city_edit.text().strip(),
                'country': self.country_edit.text().strip(),
                'description': self.description_edit.toPlainText().strip(),
                'interests': self.interests_edit.text().strip(),
                'institution': self.institution_edit.text().strip(),
                'department': self.department_edit.text().strip(),
                'idnumber': self.id_number_edit.text().strip(),
                'auth': self.auth_method_edit.currentText(),
                'timezone': self.timezone_edit.currentText(),
                'lang': self.lang_edit.currentText()
            }
            
            # Update user in Moodle
            success = self.moodle_client.update_user(self.user.get_id(), **updated_data)
            
            if success:
                # Update local user object
                self.user._first_name = updated_data['firstname']
                self.user._last_name = updated_data['lastname']
                self.user._email = updated_data['email']
                self.user._filter_content = ""  # Reset filter content
                
                # Emit signal
                self.profile_updated.emit(updated_data)
                
                QMessageBox.information(self, "Success", "Profile updated successfully!")
                logger.info(f"Profile updated for user: {self.user.get_full_name()}")
            else:
                QMessageBox.warning(self, "Update Failed", "Failed to update profile in Moodle.")
                
        except Exception as e:
            logger.error(f"Error saving profile changes: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save changes: {str(e)}")
            
    def refresh_data(self):
        """Refresh all user data"""
        try:
            self.load_user_data()
            QMessageBox.information(self, "Refreshed", "Profile data has been refreshed.")
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            QMessageBox.warning(self, "Refresh Error", f"Failed to refresh data: {str(e)}")
            
    def closeEvent(self, event):
        """Handle close event"""
        # Check if there are unsaved changes
        if self.has_unsaved_changes():
            reply = QMessageBox.question(self, "Unsaved Changes", 
                                       "You have unsaved changes. Do you want to save them?",
                                       QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if reply == QMessageBox.Save:
                self.save_changes()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
                return
        event.accept()
        
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        try:
            return (self.first_name_edit.text().strip() != self.original_data.get('firstname', '') or
                   self.last_name_edit.text().strip() != self.original_data.get('lastname', '') or
                   self.email_edit.text().strip() != self.original_data.get('email', ''))
        except:
            return False
