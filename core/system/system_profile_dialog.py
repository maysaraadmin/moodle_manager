#!/usr/bin/env python3
"""
System User Profile Dialog for Moodle Manager
Manages application-level user profiles
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import sys
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QGroupBox, 
                             QMessageBox, QFrame, QSpacerItem, QSizePolicy, 
                             QTextEdit, QProgressBar, QTabWidget, QWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QSpinBox, QFormLayout, QGridLayout,
                             QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, QDateTime
from PyQt5.QtGui import QIcon, QFont, QPalette, QPixmap, QRegExpValidator
from PyQt5.QtCore import QRegExp

from core.system.system_user_manager import SystemUserManager

logger = logging.getLogger(__name__)


class SystemProfileDialog(QDialog):
    """System user profile management dialog"""
    
    profile_updated = pyqtSignal(dict)  # Emits updated user data
    password_changed = pyqtSignal()  # Emits password change success
    
    def __init__(self, user_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.system_user_manager = SystemUserManager()
        self.user_data = user_data.copy()
        self.original_user_data = user_data.copy()
        
        self.setup_ui()
        self.load_user_data()
        
    def setup_ui(self):
        """Setup the profile dialog UI"""
        self.setWindowTitle(f"Profile - {self.user_data.get('username', 'User')}")
        self.setWindowIcon(QIcon("icons/app_icon.png") if os.path.exists("icons/app_icon.png") else QIcon())
        self.setFixedSize(600, 700)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self.create_header(main_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.create_profile_tab()
        self.create_security_tab()
        self.create_activity_tab()
        self.create_preferences_tab()
        main_layout.addWidget(self.tab_widget)
        
        # Button area
        self.create_button_area(main_layout)
        
        # Apply styling
        self.apply_modern_style()
        
    def create_header(self, parent_layout):
        """Create dialog header"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # User info
        username = self.user_data.get('username', 'Unknown')
        full_name = self.user_data.get('full_name', '')
        
        title_label = QLabel(f"User Profile")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel(f"{full_name or username}")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        parent_layout.addWidget(header_frame)
        
    def create_profile_tab(self):
        """Create profile information tab"""
        profile_tab = QWidget()
        profile_layout = QVBoxLayout(profile_tab)
        profile_layout.setSpacing(15)
        
        # Personal information group
        personal_group = QGroupBox("Personal Information")
        personal_layout = QFormLayout(personal_group)
        
        # Username (read-only)
        self.username_display = QLineEdit()
        self.username_display.setReadOnly(True)
        self.username_display.setStyleSheet("background-color: #f8f9fa;")
        personal_layout.addRow("Username:", self.username_display)
        
        # Full name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Enter your full name")
        personal_layout.addRow("Full Name:", self.full_name_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        # Email validation
        email_regex = QRegExp(r"[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}")
        email_validator = QRegExpValidator(email_regex)
        self.email_input.setValidator(email_validator)
        personal_layout.addRow("Email:", self.email_input)
        
        # Role (read-only for non-admins)
        self.role_display = QLineEdit()
        self.role_display.setReadOnly(True)
        self.role_display.setStyleSheet("background-color: #f8f9fa;")
        personal_layout.addRow("Role:", self.role_display)
        
        # Account status
        self.status_display = QLineEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setStyleSheet("background-color: #f8f9fa;")
        personal_layout.addRow("Status:", self.status_display)
        
        profile_layout.addWidget(personal_group)
        
        # Account information group
        account_group = QGroupBox("Account Information")
        account_layout = QFormLayout(account_group)
        
        # Created date
        self.created_display = QLineEdit()
        self.created_display.setReadOnly(True)
        self.created_display.setStyleSheet("background-color: #f8f9fa;")
        account_layout.addRow("Member Since:", self.created_display)
        
        # Last login
        self.last_login_display = QLineEdit()
        self.last_login_display.setReadOnly(True)
        self.last_login_display.setStyleSheet("background-color: #f8f9fa;")
        account_layout.addRow("Last Login:", self.last_login_display)
        
        profile_layout.addWidget(account_group)
        profile_layout.addStretch()
        
        self.tab_widget.addTab(profile_tab, "Profile")
        
    def create_security_tab(self):
        """Create security settings tab"""
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setSpacing(15)
        
        # Password change group
        password_group = QGroupBox("Change Password")
        password_layout = QVBoxLayout(password_group)
        
        # Current password
        current_password_layout = QHBoxLayout()
        current_password_label = QLabel("Current Password:")
        current_password_label.setFixedWidth(120)
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.Password)
        self.current_password_input.setPlaceholderText("Enter current password")
        current_password_layout.addWidget(current_password_label)
        current_password_layout.addWidget(self.current_password_input)
        password_layout.addLayout(current_password_layout)
        
        # New password
        new_password_layout = QHBoxLayout()
        new_password_label = QLabel("New Password:")
        new_password_label.setFixedWidth(120)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("Enter new password")
        new_password_layout.addWidget(new_password_label)
        new_password_layout.addWidget(self.new_password_input)
        password_layout.addLayout(new_password_layout)
        
        # Confirm new password
        confirm_password_layout = QHBoxLayout()
        confirm_password_label = QLabel("Confirm Password:")
        confirm_password_label.setFixedWidth(120)
        self.confirm_new_password_input = QLineEdit()
        self.confirm_new_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_new_password_input.setPlaceholderText("Confirm new password")
        confirm_password_layout.addWidget(confirm_password_label)
        confirm_password_layout.addWidget(self.confirm_new_password_input)
        password_layout.addLayout(confirm_password_layout)
        
        # Change password button
        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.clicked.connect(self.change_password)
        password_layout.addWidget(self.change_password_button)
        
        security_layout.addWidget(password_group)
        
        # Security info group
        security_info_group = QGroupBox("Security Information")
        security_info_layout = QFormLayout(security_info_group)
        
        # Admin status
        self.admin_status_display = QLineEdit()
        self.admin_status_display.setReadOnly(True)
        self.admin_status_display.setStyleSheet("background-color: #f8f9fa;")
        security_info_layout.addRow("Administrator:", self.admin_status_display)
        
        # Active sessions
        self.sessions_display = QLineEdit()
        self.sessions_display.setReadOnly(True)
        self.sessions_display.setStyleSheet("background-color: #f8f9fa;")
        security_info_layout.addRow("Active Sessions:", self.sessions_display)
        
        security_layout.addWidget(security_info_group)
        security_layout.addStretch()
        
        self.tab_widget.addTab(security_tab, "Security")
        
    def create_activity_tab(self):
        """Create user activity tab"""
        activity_tab = QWidget()
        activity_layout = QVBoxLayout(activity_tab)
        activity_layout.setSpacing(15)
        
        # Activity log group
        activity_group = QGroupBox("Recent Activity")
        activity_group_layout = QVBoxLayout(activity_group)
        
        # Activity table
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Activity", "Details", "IP Address", "Timestamp"])
        
        # Configure table
        header = self.activity_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.activity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        activity_group_layout.addWidget(self.activity_table)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Activity")
        refresh_button.clicked.connect(self.load_activity_data)
        activity_group_layout.addWidget(refresh_button)
        
        activity_layout.addWidget(activity_group)
        
        self.tab_widget.addTab(activity_tab, "Activity")
        
    def create_preferences_tab(self):
        """Create user preferences tab"""
        preferences_tab = QWidget()
        preferences_layout = QVBoxLayout(preferences_tab)
        preferences_layout.setSpacing(15)
        
        # General preferences group
        general_group = QGroupBox("General Preferences")
        general_layout = QFormLayout(general_group)
        
        # Theme preference
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        general_layout.addRow("Theme:", self.theme_combo)
        
        # Language preference
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German"])
        general_layout.addRow("Language:", self.language_combo)
        
        # Remember credentials
        self.remember_credentials_checkbox = QCheckBox("Remember Moodle credentials")
        general_layout.addRow("", self.remember_credentials_checkbox)
        
        preferences_layout.addWidget(general_group)
        
        # Notification preferences group
        notification_group = QGroupBox("Notification Preferences")
        notification_layout = QFormLayout(notification_group)
        
        # Enable notifications
        self.enable_notifications_checkbox = QCheckBox("Enable desktop notifications")
        notification_layout.addRow("", self.enable_notifications_checkbox)
        
        # Error notifications
        self.error_notifications_checkbox = QCheckBox("Notify on errors")
        notification_layout.addRow("", self.error_notifications_checkbox)
        
        preferences_layout.addWidget(notification_group)
        preferences_layout.addStretch()
        
        self.tab_widget.addTab(preferences_tab, "Preferences")
        
    def create_button_area(self, parent_layout):
        """Create button area"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.save_button)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        parent_layout.addLayout(button_layout)
        
    def load_user_data(self):
        """Load user data into form fields"""
        # Profile tab
        self.username_display.setText(self.user_data.get('username', ''))
        self.full_name_input.setText(self.user_data.get('full_name', ''))
        self.email_input.setText(self.user_data.get('email', ''))
        self.role_display.setText(self.user_data.get('role', 'user').title())
        
        # Status
        status = "Active" if self.user_data.get('is_active', False) else "Inactive"
        self.status_display.setText(status)
        
        # Account info
        created_date = self.user_data.get('created_at', '')
        if created_date:
            try:
                dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                self.created_display.setText(dt.strftime('%B %d, %Y'))
            except:
                self.created_display.setText(created_date)
        
        last_login = self.user_data.get('last_login', '')
        if last_login:
            try:
                dt = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
                self.last_login_display.setText(dt.strftime('%B %d, %Y at %I:%M %p'))
            except:
                self.last_login_display.setText("Never")
        else:
            self.last_login_display.setText("Never")
        
        # Security tab
        admin_status = "Yes" if self.user_data.get('is_admin', False) else "No"
        self.admin_status_display.setText(admin_status)
        
        # Load active sessions count
        stats = self.system_user_manager.get_system_stats()
        self.sessions_display.setText(str(stats.get('active_sessions', 0)))
        
        # Load preferences
        self.load_preferences()
        
        # Load activity data
        self.load_activity_data()
        
    def load_preferences(self):
        """Load user preferences"""
        user_id = self.user_data.get('id')
        if not user_id:
            return
            
        # Load theme preference
        theme = self.system_user_manager.get_user_preference(user_id, 'theme', 'Light')
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Load language preference
        language = self.system_user_manager.get_user_preference(user_id, 'language', 'English')
        index = self.language_combo.findText(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        # Load checkbox preferences
        self.remember_credentials_checkbox.setChecked(
            self.system_user_manager.get_user_preference(user_id, 'remember_credentials', False)
        )
        self.enable_notifications_checkbox.setChecked(
            self.system_user_manager.get_user_preference(user_id, 'enable_notifications', True)
        )
        self.error_notifications_checkbox.setChecked(
            self.system_user_manager.get_user_preference(user_id, 'error_notifications', True)
        )
        
    def load_activity_data(self):
        """Load user activity data"""
        user_id = self.user_data.get('id')
        if not user_id:
            return
            
        activities = self.system_user_manager.get_user_activity(user_id, limit=20)
        
        self.activity_table.setRowCount(len(activities))
        
        for row, activity in enumerate(activities):
            # Activity type
            activity_item = QTableWidgetItem(activity.get('activity_type', ''))
            self.activity_table.setItem(row, 0, activity_item)
            
            # Details
            details_item = QTableWidgetItem(activity.get('activity_details', ''))
            self.activity_table.setItem(row, 1, details_item)
            
            # IP Address
            ip_item = QTableWidgetItem(activity.get('ip_address', 'N/A'))
            self.activity_table.setItem(row, 2, ip_item)
            
            # Timestamp
            timestamp = activity.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_time = timestamp
            else:
                formatted_time = 'N/A'
            
            time_item = QTableWidgetItem(formatted_time)
            self.activity_table.setItem(row, 3, time_item)
            
    def save_changes(self):
        """Save profile changes"""
        # Validate inputs
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        
        errors = []
        if not full_name:
            errors.append("Full name is required")
        if not email:
            errors.append("Email is required")
        elif '@' not in email:
            errors.append("Invalid email format")
            
        if errors:
            QMessageBox.warning(self, "Validation Error", "\\n".join(errors))
            return
            
        # Update user data
        user_id = self.user_data.get('id')
        if user_id:
            success = self.system_user_manager.update_user(
                user_id,
                full_name=full_name,
                email=email
            )
            
            if success:
                # Update local user data
                self.user_data['full_name'] = full_name
                self.user_data['email'] = email
                
                # Save preferences
                self.save_preferences()
                
                # Emit signal
                self.profile_updated.emit(self.user_data)
                
                QMessageBox.information(self, "Success", "Profile updated successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update profile")
                
    def save_preferences(self):
        """Save user preferences"""
        user_id = self.user_data.get('id')
        if not user_id:
            return
            
        preferences = {
            'theme': self.theme_combo.currentText(),
            'language': self.language_combo.currentText(),
            'remember_credentials': self.remember_credentials_checkbox.isChecked(),
            'enable_notifications': self.enable_notifications_checkbox.isChecked(),
            'error_notifications': self.error_notifications_checkbox.isChecked()
        }
        
        for key, value in preferences.items():
            self.system_user_manager.set_user_preference(user_id, key, value)
            
    def change_password(self):
        """Change user password"""
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_new_password_input.text()
        
        # Validation
        errors = []
        if not current_password:
            errors.append("Current password is required")
        if not new_password:
            errors.append("New password is required")
        if len(new_password) < 6:
            errors.append("Password must be at least 6 characters")
        if new_password != confirm_password:
            errors.append("Passwords do not match")
            
        if errors:
            QMessageBox.warning(self, "Validation Error", "\\n".join(errors))
            return
            
        # Verify current password by attempting authentication
        username = self.user_data.get('username')
        if not self.system_user_manager.authenticate_user(username, current_password):
            QMessageBox.critical(self, "Error", "Current password is incorrect")
            return
            
        # Change password
        user_id = self.user_data.get('id')
        if user_id and self.system_user_manager.change_password(user_id, new_password):
            # Clear password fields
            self.current_password_input.clear()
            self.new_password_input.clear()
            self.confirm_new_password_input.clear()
            
            # Emit signal
            self.password_changed.emit()
            
            QMessageBox.information(self, "Success", "Password changed successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to change password")
            
    def apply_modern_style(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
            
            QLineEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 10pt;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QLineEdit[readOnly="true"] {
                background-color: #f8f9fa;
                color: #6c757d;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QCheckBox {
                color: #495057;
            }
            
            QComboBox {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                min-width: 150px;
            }
            
            QComboBox:focus {
                border-color: #007bff;
            }
            
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
                border-radius: 6px;
            }
            
            QTabBar::tab {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #007bff;
                color: white;
            }
            
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                gridline-color: #e9ecef;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-right: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)
