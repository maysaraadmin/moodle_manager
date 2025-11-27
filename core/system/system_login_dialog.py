#!/usr/bin/env python3
"""
System Login Dialog for Moodle Manager
Handles application-level user authentication
"""

import sys
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QGroupBox, 
                             QMessageBox, QFrame, QSpacerItem, QSizePolicy, 
                             QTextEdit, QProgressBar, QTabWidget, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QIcon, QFont, QPalette, QPixmap

from core.system.system_user_manager import SystemUserManager

logger = logging.getLogger(__name__)


class SystemLoginDialog(QDialog):
    """System-level login dialog for application authentication"""
    
    login_successful = pyqtSignal(dict)  # Emits user data
    login_failed = pyqtSignal(str)  # Emits error message
    registration_requested = pyqtSignal()  # Emits registration request
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.system_user_manager = SystemUserManager()
        self.current_user = None
        self.session_token = None
        
        self.setup_ui()
        self.setup_connections()
        self.load_remembered_user()
        
    def setup_ui(self):
        """Setup the system login dialog UI"""
        self.setWindowTitle("Moodle Manager - System Login")
        self.setWindowIcon(QIcon("icons/app_icon.png") if os.path.exists("icons/app_icon.png") else QIcon())
        self.setFixedSize(450, 600)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # App header
        self.create_app_header(main_layout)
        
        # Tab widget for login and registration
        self.tab_widget = QTabWidget()
        self.create_login_tab()
        self.create_registration_tab()
        main_layout.addWidget(self.tab_widget)
        
        # Status area
        self.create_status_area(main_layout)
        
        # Apply modern styling
        self.apply_modern_style()
        
    def create_app_header(self, parent_layout):
        """Create application header"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # App title
        title_label = QLabel("Moodle Manager")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        
        # Subtitle
        subtitle_label = QLabel("System Authentication")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        parent_layout.addWidget(header_frame)
        
    def create_login_tab(self):
        """Create login tab"""
        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)
        login_layout.setSpacing(15)
        
        # Login form group
        login_group = QGroupBox("Sign In")
        login_group.setFont(QFont("Arial", 11, QFont.Bold))
        login_form = QVBoxLayout(login_group)
        
        # Username field
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setFixedWidth(100)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFont(QFont("Arial", 10))
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        login_form.addLayout(username_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFixedWidth(100)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setFont(QFont("Arial", 10))
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        login_form.addLayout(password_layout)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setFont(QFont("Arial", 9))
        login_form.addWidget(self.remember_checkbox)
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.login_button.setFixedHeight(40)
        login_form.addWidget(self.login_button)
        
        # Forgot password link
        forgot_password_layout = QHBoxLayout()
        forgot_password_layout.addStretch()
        forgot_password_label = QLabel("Forgot Password?")
        forgot_password_label.setStyleSheet("color: #3498db; text-decoration: underline;")
        forgot_password_label.setCursor(Qt.PointingHandCursor)
        forgot_password_label.mousePressEvent = self.on_forgot_password
        forgot_password_layout.addWidget(forgot_password_label)
        forgot_password_layout.addStretch()
        login_form.addLayout(forgot_password_layout)
        
        login_layout.addWidget(login_group)
        login_layout.addStretch()
        
        self.tab_widget.addTab(login_tab, "Sign In")
        
    def create_registration_tab(self):
        """Create registration tab"""
        registration_tab = QWidget()
        registration_layout = QVBoxLayout(registration_tab)
        registration_layout.setSpacing(15)
        
        # Registration form group
        registration_group = QGroupBox("Create Account")
        registration_group.setFont(QFont("Arial", 11, QFont.Bold))
        registration_form = QVBoxLayout(registration_group)
        
        # Username field
        reg_username_layout = QHBoxLayout()
        reg_username_label = QLabel("Username:")
        reg_username_label.setFixedWidth(100)
        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText("Choose a username")
        self.reg_username_input.setFont(QFont("Arial", 10))
        reg_username_layout.addWidget(reg_username_label)
        reg_username_layout.addWidget(self.reg_username_input)
        registration_form.addLayout(reg_username_layout)
        
        # Email field
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setFixedWidth(100)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setFont(QFont("Arial", 10))
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        registration_form.addLayout(email_layout)
        
        # Full name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Full Name:")
        name_label.setFixedWidth(100)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        self.name_input.setFont(QFont("Arial", 10))
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        registration_form.addLayout(name_layout)
        
        # Password field
        reg_password_layout = QHBoxLayout()
        reg_password_label = QLabel("Password:")
        reg_password_label.setFixedWidth(100)
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_password_input.setPlaceholderText("Create a password")
        self.reg_password_input.setFont(QFont("Arial", 10))
        reg_password_layout.addWidget(reg_password_label)
        reg_password_layout.addWidget(self.reg_password_input)
        registration_form.addLayout(reg_password_layout)
        
        # Confirm password field
        confirm_password_layout = QHBoxLayout()
        confirm_password_label = QLabel("Confirm:")
        confirm_password_label.setFixedWidth(100)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setFont(QFont("Arial", 10))
        confirm_password_layout.addWidget(confirm_password_label)
        confirm_password_layout.addWidget(self.confirm_password_input)
        registration_form.addLayout(confirm_password_layout)
        
        # Register button
        self.register_button = QPushButton("Create Account")
        self.register_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.register_button.setFixedHeight(40)
        registration_form.addWidget(self.register_button)
        
        registration_layout.addWidget(registration_group)
        registration_layout.addStretch()
        
        self.tab_widget.addTab(registration_tab, "Register")
        
    def create_status_area(self, parent_layout):
        """Create status area"""
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        
        # Status label
        self.status_label = QLabel("Please sign in to access the application")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("color: #7f8c8d;")
        status_layout.addWidget(self.status_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(4)
        status_layout.addWidget(self.progress_bar)
        
        parent_layout.addWidget(status_frame)
        
    def setup_connections(self):
        """Setup signal connections"""
        # Login connections
        self.login_button.clicked.connect(self.attempt_login)
        self.username_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)
        
        # Registration connections
        self.register_button.clicked.connect(self.attempt_registration)
        
        # Tab change
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
    def apply_modern_style(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
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
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
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
            
            QProgressBar {
                border: none;
                background-color: #e9ecef;
                border-radius: 2px;
            }
            
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 2px;
            }
        """)
        
    def on_tab_changed(self, index):
        """Handle tab change"""
        if index == 0:  # Login tab
            self.status_label.setText("Please sign in to access the application")
        else:  # Registration tab
            self.status_label.setText("Create a new account to access the application")
            
    def attempt_login(self):
        """Attempt system login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
            
        self.show_progress("Authenticating...")
        
        # Authenticate user
        user_data = self.system_user_manager.authenticate_user(username, password)
        
        if user_data:
            # Create session
            self.session_token = self.system_user_manager.create_session(
                user_data['id'], 
                ip_address="127.0.0.1",  # Could get real IP
                user_agent="MoodleManager"
            )
            
            if self.session_token:
                self.current_user = user_data
                self.show_success("Login successful!")
                
                # Remember me if checked
                if self.remember_checkbox.isChecked():
                    self.save_remembered_user(username)
                
                # Emit success signal
                QTimer.singleShot(500, lambda: self.on_login_success_complete({
                    'user': user_data,
                    'session_token': self.session_token
                }))
            else:
                self.show_error("Failed to create session")
        else:
            self.show_error("Invalid username or password")
            
    def on_login_success_complete(self, system_data):
        """Complete the login process by emitting signal and closing dialog"""
        self.login_successful.emit(system_data)
        self.accept()  # Close the dialog
        
    def attempt_registration(self):
        """Attempt user registration"""
        username = self.reg_username_input.text().strip()
        email = self.email_input.text().strip()
        full_name = self.name_input.text().strip()
        password = self.reg_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validation
        errors = []
        if not username:
            errors.append("Username is required")
        if not email:
            errors.append("Email is required")
        if not full_name:
            errors.append("Full name is required")
        if not password:
            errors.append("Password is required")
        if password != confirm_password:
            errors.append("Passwords do not match")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters")
            
        if errors:
            self.show_error("\\n".join(errors))
            return
            
        self.show_progress("Creating account...")
        
        # Create user
        success = self.system_user_manager.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role='user'
        )
        
        if success:
            self.show_success("Account created successfully!")
            
            # Switch to login tab and pre-fill username
            self.tab_widget.setCurrentIndex(0)
            self.username_input.setText(username)
            self.password_input.setFocus()
            
            # Clear registration form
            self.clear_registration_form()
        else:
            self.show_error("Failed to create account. Username or email may already exist.")
            
    def clear_registration_form(self):
        """Clear registration form fields"""
        self.reg_username_input.clear()
        self.email_input.clear()
        self.name_input.clear()
        self.reg_password_input.clear()
        self.confirm_password_input.clear()
        
    def save_remembered_user(self, username):
        """Save remembered username"""
        try:
            with open(os.path.join(os.path.dirname(__file__), '.remembered_user'), 'w') as f:
                f.write(username)
        except:
            pass  # Ignore errors
            
    def load_remembered_user(self):
        """Load remembered username"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), '.remembered_user')
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    username = f.read().strip()
                    if username:
                        self.username_input.setText(username)
                        self.remember_checkbox.setChecked(True)
        except:
            pass  # Ignore errors
            
    def on_forgot_password(self, event):
        """Handle forgot password click"""
        QMessageBox.information(self, "Forgot Password", 
                              "Please contact your system administrator to reset your password.")
        
    def show_progress(self, message):
        """Show progress indicator"""
        self.status_label.setText(message)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
    def show_success(self, message):
        """Show success message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #28a745;")
        self.progress_bar.setVisible(False)
        
    def show_error(self, message):
        """Show error message"""
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: #dc3545;")
        self.progress_bar.setVisible(False)
        
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        return self.current_user
        
    def get_session_token(self) -> Optional[str]:
        """Get current session token"""
        return self.session_token
        
    def closeEvent(self, event):
        """Handle dialog close event"""
        # Clean up session if exists
        if self.session_token:
            self.system_user_manager.destroy_session(self.session_token)
        event.accept()
