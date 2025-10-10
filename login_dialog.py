"""
Enhanced Login Dialog for Moodle Manager
Provides secure login interface with remember me functionality
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QCheckBox, QGroupBox, QProgressBar, 
                             QMessageBox, QFrame, QSpacerItem, QSizePolicy, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QIcon, QFont, QPalette
import os
import sys
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime
from auth_manager import AuthManager
from connection_validator import ConnectionValidator
from config_manager import ConfigManager

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    
    login_successful = pyqtSignal(dict)  # Emits connection details
    login_failed = pyqtSignal(str)  # Emits error message
    credentials_stored = pyqtSignal(bool)  # Emits whether credentials were stored
    
    def __init__(self, parent=None, auth_manager: AuthManager = None):
        super().__init__()
        self.auth_manager = auth_manager or AuthManager("MoodleManager")
        self.config_manager = ConfigManager()
        self.connection_validator = ConnectionValidator(self.auth_manager)
        self.connection_worker = None
        self.diagnostics_mode = False
        self.setup_ui()
        self.load_config()
        self.load_saved_credentials()
        
    def setup_ui(self):
        """Setup the login dialog UI"""
        self.setWindowTitle("Moodle Manager - Login")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Login to Moodle")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Connection settings group
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QVBoxLayout()
        
        # Host input
        host_layout = QHBoxLayout()
        host_label = QLabel("Moodle URL:")
        host_label.setMinimumWidth(80)
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("https://your-moodle-site.com")
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        connection_layout.addLayout(host_layout)
        
        # Service input
        service_layout = QHBoxLayout()
        service_label = QLabel("Service:")
        service_label.setMinimumWidth(80)
        self.service_input = QLineEdit()
        self.service_input.setPlaceholderText("moodle_mobile_app")
        self.service_input.setText("moodle_mobile_app")
        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_input)
        connection_layout.addLayout(service_layout)
        
        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)
        
        # Credentials group
        credentials_group = QGroupBox("Credentials")
        credentials_layout = QVBoxLayout()
        
        # Username input
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setMinimumWidth(80)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        credentials_layout.addLayout(username_layout)
        
        # Password input
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setMinimumWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        credentials_layout.addLayout(password_layout)
        
        # Remember me checkbox
        self.remember_me_checkbox = QCheckBox("Remember me (store credentials securely)")
        self.remember_me_checkbox.setToolTip("Store your credentials encrypted for automatic login")
        credentials_layout.addWidget(self.remember_me_checkbox)
        
        credentials_group.setLayout(credentials_layout)
        main_layout.addWidget(credentials_group)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status label (initially hidden)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666;")
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)
        
        # Diagnostics text area (initially hidden)
        self.diagnostics_text = QTextEdit()
        self.diagnostics_text.setReadOnly(True)
        self.diagnostics_text.setMaximumHeight(150)
        self.diagnostics_text.setStyleSheet("background-color: #f5f5f5; font-family: monospace; font-size: 9pt;")
        self.diagnostics_text.setVisible(False)
        main_layout.addWidget(self.diagnostics_text)
        
        # Diagnostics button
        self.diagnostics_button = QPushButton("Show Diagnostics")
        self.diagnostics_button.setCheckable(True)
        self.diagnostics_button.clicked.connect(self.toggle_diagnostics)
        self.diagnostics_button.setVisible(False)
        main_layout.addWidget(self.diagnostics_button)
        
        # MFA group (initially hidden)
        self.mfa_group = QGroupBox("Multi-Factor Authentication")
        mfa_layout = QVBoxLayout()
        
        # MFA info label
        self.mfa_info_label = QLabel("Enter the verification code from your authenticator app:")
        mfa_layout.addWidget(self.mfa_info_label)
        
        # MFA code input
        mfa_code_layout = QHBoxLayout()
        mfa_code_label = QLabel("Verification Code:")
        mfa_code_label.setMinimumWidth(120)
        self.mfa_code_input = QLineEdit()
        self.mfa_code_input.setPlaceholderText("Enter 6-digit code")
        self.mfa_code_input.setMaxLength(6)
        mfa_code_layout.addWidget(mfa_code_label)
        mfa_code_layout.addWidget(self.mfa_code_input)
        mfa_layout.addLayout(mfa_code_layout)
        
        # MFA backup code section
        self.mfa_backup_label = QLabel("Or enter a backup code:")
        mfa_layout.addWidget(self.mfa_backup_label)
        
        self.mfa_group.setLayout(mfa_layout)
        self.mfa_group.setVisible(False)
        main_layout.addWidget(self.mfa_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.attempt_login)
        
        # Test Connection button
        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_connection_button)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Set focus to username input
        self.username_input.setFocus()
        
        # Connect enter key to login
        self.host_input.returnPressed.connect(self.attempt_login)
        self.service_input.returnPressed.connect(self.attempt_login)
        self.username_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)
        
    def load_saved_credentials(self):
        """Load saved credentials if available"""
        try:
            # Get list of saved credentials
            saved_credentials = self.auth_manager.get_all_credentials()
            
            if saved_credentials:
                # If there's only one saved credential, auto-fill it
                if len(saved_credentials) == 1:
                    credential = list(saved_credentials.values())[0]
                    host = credential.get('host', '')
                    username = credential.get('username', '')
                    service = credential.get('service', 'moodle_mobile_app')
                    
                    # Validate the credential format
                    is_valid, validation_msg = self.auth_manager.validate_credentials_format(username, "dummy_password")
                    if not is_valid and "Username cannot be empty" in validation_msg:
                        # Invalid credentials found, clear them
                        logger.warning(f"Found invalid stored credentials for {host}, clearing them")
                        self.auth_manager.delete_credentials(host, username)
                        QMessageBox.information(self, "Invalid Credentials", 
                                              "Found invalid stored credentials. They have been cleared. Please login again.")
                        return
                    
                    self.host_input.setText(host)
                    self.username_input.setText(username)
                    self.service_input.setText(service)
                    self.remember_me_checkbox.setChecked(credential.get('remember_me', False))
                    logger.info("Auto-filled saved credentials")
                else:
                    # Multiple credentials - don't auto-fill, let user choose
                    logger.info(f"Found {len(saved_credentials)} saved credentials")
            
        except Exception as e:
            logger.error(f"Error loading saved credentials: {e}")
    
    def load_config(self):
        """Load configuration settings from config file"""
        try:
            # Load config from standard locations
            config_path = os.path.join(os.path.dirname(sys.executable), 'config.ini')
            if not os.path.exists(config_path):
                config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

            if os.path.exists(config_path):
                self.config_manager.load_config(config_path)
                logger.info(f"Configuration loaded from {config_path}")

                # Load first available LMS configuration
                all_configs = self.config_manager.get_all_configs()
                if all_configs:
                    # Use the first configuration found
                    first_config_section = list(all_configs.keys())[0]
                    config = all_configs[first_config_section]

                    # Pre-populate form fields with config values
                    if config.url:
                        self.host_input.setText(config.url)
                    if config.username:
                        self.username_input.setText(config.username)
                    if config.service:
                        self.service_input.setText(config.service)
                    if config.remember_me:
                        self.remember_me_checkbox.setChecked(True)

                    logger.info(f"Pre-populated login form with config: {config.name}")
                else:
                    logger.info("No LMS configurations found in config file")
            else:
                logger.info("No configuration file found")

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

    def load_saved_credentials(self):
        """Load saved credentials if available"""
        try:
            # Get list of saved credentials
            saved_credentials = self.auth_manager.get_all_credentials()
            
            if saved_credentials:
                # If there's only one saved credential, auto-fill it
                if len(saved_credentials) == 1:
                    credential = list(saved_credentials.values())[0]
                    host = credential.get('host', '')
                    username = credential.get('username', '')
                    service = credential.get('service', 'moodle_mobile_app')
                    
                    # Validate the credential format
                    is_valid, validation_msg = self.auth_manager.validate_credentials_format(username, "dummy_password")
                    if not is_valid and "Username cannot be empty" in validation_msg:
                        # Invalid credentials found, clear them
                        logger.warning(f"Found invalid stored credentials for {host}, clearing them")
                        self.auth_manager.delete_credentials(host, username)
                        QMessageBox.information(self, "Invalid Credentials", 
                                              "Found invalid stored credentials. They have been cleared. Please login again.")
                        return
                    
                    self.host_input.setText(host)
                    self.username_input.setText(username)
                    self.service_input.setText(service)
                    self.remember_me_checkbox.setChecked(credential.get('remember_me', False))
                    logger.info("Auto-filled saved credentials")
                else:
                    # Multiple credentials - don't auto-fill, let user choose
                    logger.info(f"Found {len(saved_credentials)} saved credentials")
            
        except Exception as e:
            # Handle credential decryption errors gracefully
            if "Incorrect padding" in str(e) or "Failed to retrieve credentials" in str(e):
                logger.warning(f"Corrupted credentials detected, clearing credential store: {e}")
                # Clear all corrupted credentials and continue
                try:
                    # Try to clear the credential store
                    self.auth_manager.clear_all_credentials()
                except:
                    pass  # Ignore errors when clearing
                logger.info("Cleared corrupted credentials, user can login fresh")
            else:
                logger.error(f"Error loading saved credentials: {e}")
    
    def validate_inputs(self) -> bool:
        errors = []
        
        # Validate host
        host = self.host_input.text().strip()
        if not host:
            errors.append("Moodle URL is required")
        elif not (host.startswith('http://') or host.startswith('https://')):
            errors.append("Moodle URL must start with http:// or https://")
        
        # Validate username
        username = self.username_input.text().strip()
        if not username:
            errors.append("Username is required")
        
        # Validate password
        password = self.password_input.text()
        if not password:
            errors.append("Password is required")
        
        # Validate service
        service = self.service_input.text().strip()
        if not service:
            errors.append("Service name is required")
        
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return False
        
    def quick_validate_connection(self, host: str, username: str, password: str, service: str) -> bool:
        """Quick validation of URL accessibility and credential correctness"""
        try:
            # Step 1: Test basic URL accessibility
            self.status_label.setText("Testing Moodle URL accessibility...")
            self.status_label.setStyleSheet("color: #1976d2;")
            self.status_label.setVisible(True)

            try:
                # Test if we can reach the Moodle server
                response = requests.get(host, timeout=5)
                if response.status_code != 200:
                    QMessageBox.warning(self, "URL Not Accessible",
                                      f"Cannot access Moodle server at {host}.\n\nHTTP Status: {response.status_code}\n\nPlease check:\n• Moodle server is running\n• URL is correct\n• Network connection is working")
                    return False
            except requests.exceptions.ConnectionError:
                QMessageBox.warning(self, "Connection Error",
                                  f"Cannot connect to Moodle server at {host}.\n\nPlease check:\n• Moodle server is running\n• URL is correct\n• Firewall settings\n• Network connectivity")
                return False
            except requests.exceptions.Timeout:
                QMessageBox.warning(self, "Connection Timeout",
                                  f"Connection to Moodle server at {host} timed out.\n\nPlease check:\n• Moodle server is responding\n• Network connection is stable\n• Server is not overloaded")
                return False
            except Exception as e:
                QMessageBox.warning(self, "URL Test Error",
                                  f"Error testing Moodle URL {host}:\n\n{str(e)}\n\nPlease check your connection and try again.")
                return False

            # Step 2: Test credential validity
            self.status_label.setText("Validating credentials...")

            # Try to get a token to validate credentials
            token_url = f"{host}/login/token.php"
            token_data = {
                'username': username,
                'password': password,
                'service': service
            }

            try:
                token_response = requests.post(token_url, data=token_data, timeout=10)

                if token_response.status_code == 200:
                    token_result = token_response.json()

                    if 'token' in token_result:
                        # Credentials are valid
                        self.status_label.setText("Credentials validated successfully!")
                        self.status_label.setStyleSheet("color: #4caf50;")
                        QTimer.singleShot(1000, lambda: self.status_label.setVisible(False))
                        return True
                    else:
                        # Invalid credentials
                        error_msg = token_result.get('error', 'Invalid credentials')
                        QMessageBox.warning(self, "Invalid Credentials",
                                          f"Username or password is incorrect.\n\nError: {error_msg}\n\nPlease check:\n• Username is correct\n• Password is correct\n• Account is active\n• Caps Lock is off")
                        return False
                else:
                    QMessageBox.warning(self, "Authentication Error",
                                      f"Authentication service error (HTTP {token_response.status_code}).\n\nPlease check:\n• Moodle web services are enabled\n• Service name is correct\n• User has web service permissions")
                    return False

            except requests.exceptions.ConnectionError:
                QMessageBox.warning(self, "Connection Error",
                                  "Cannot connect to Moodle authentication service.\n\nPlease check your connection and Moodle server status.")
                return False
            except requests.exceptions.Timeout:
                QMessageBox.warning(self, "Timeout Error",
                                  "Authentication request timed out.\n\nPlease check Moodle server performance.")
                return False
            except Exception as e:
                QMessageBox.warning(self, "Authentication Test Error",
                                  f"Error testing authentication:\n\n{str(e)}\n\nPlease try again or contact your administrator.")
                return False

        except Exception as e:
            logger.error(f"Quick validation error: {e}")
            QMessageBox.critical(self, "Validation Error",
                               f"An unexpected error occurred during validation:\n\n{str(e)}")
            return False

    def attempt_login(self):
        """Attempt to login with provided credentials"""
        if not self.validate_inputs():
            return
        
        # Get input values
        host = self.host_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        service = self.service_input.text().strip()
        remember_me = self.remember_me_checkbox.isChecked()
        
        # Pre-validate URL and credentials before full authentication
        if not self.quick_validate_connection(host, username, password, service):
            return
        
        # Check if MFA is required
        mfa_status = self.auth_manager.get_mfa_status(host, username)
        
        if mfa_status.get('enabled', False):
            # MFA is enabled, show MFA input
            self.show_mfa_input()
            return
        
        # Proceed with normal login
        self.proceed_with_login(host, username, password, service, remember_me)
    
    def show_mfa_input(self):
        """Show MFA input fields"""
        self.mfa_group.setVisible(True)
        self.mfa_group.setEnabled(True)
        self.mfa_code_input.clear()
        self.mfa_code_input.setFocus()
        
        # Update UI
        self.credentials_group.setEnabled(False)
        self.connection_group.setEnabled(False)
        self.login_button.setText("Verify")
        
        # Connect MFA input events
        self.mfa_code_input.returnPressed.connect(self.verify_mfa)
    
    def verify_mfa(self):
        """Verify MFA code and proceed with login"""
        # Get input values
        host = self.host_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        service = self.service_input.text().strip()
        remember_me = self.remember_me_checkbox.isChecked()
        mfa_code = self.mfa_code_input.text().strip()
        
        if not mfa_code:
            QMessageBox.warning(self, "MFA Required", "Please enter the verification code")
            return
        
        # Validate MFA code
        if not self.auth_manager.validate_mfa_code(host, username, mfa_code):
            QMessageBox.warning(self, "MFA Failed", "Invalid verification code. Please try again.")
            self.mfa_code_input.clear()
            self.mfa_code_input.setFocus()
            return
        
        # MFA validated, proceed with login
        self.proceed_with_login(host, username, password, service, remember_me)
    
    def proceed_with_login(self, host: str, username: str, password: str, service: str, remember_me: bool):
        """Proceed with the actual login process"""
        # Show progress
        self.set_ui_state(True)
        self.status_label.setText("Running comprehensive connection test...")
        self.status_label.setStyleSheet("color: #1976d2;")
        self.status_label.setVisible(True)
        
        # Show diagnostics button
        self.diagnostics_button.setVisible(True)
        
        # Use connection validator for comprehensive testing
        self.status_label.setText("Validating parameters...")
        
        # Run comprehensive test in a separate thread to avoid blocking UI
        self.comprehensive_test_thread = ComprehensiveTestThread(
            self.connection_validator, host, username, password, service
        )
        self.comprehensive_test_thread.finished.connect(self.on_comprehensive_test_finished)
        self.comprehensive_test_thread.error.connect(self.on_comprehensive_test_error)
        self.comprehensive_test_thread.progress.connect(self.on_test_progress)
        self.comprehensive_test_thread.start()
        
        logger.info(f"Starting comprehensive connection test for {username}@{host}")
    
    def on_test_progress(self, message: str):
        """Handle test progress updates"""
        self.status_label.setText(message)
        self._add_diagnostics_message(f"PROGRESS: {message}")
    
    def on_comprehensive_test_finished(self, test_result: Dict[str, Any]):
        """Handle comprehensive test completion"""
        if test_result['success']:
            # All tests passed, proceed with actual login
            self.status_label.setText("Connection test passed. Authenticating...")
            self.status_label.setStyleSheet("color: #4caf50;")
            self._add_diagnostics_message("SUCCESS: All connection tests passed")
            
            # Get the validated parameters
            host = self.host_input.text().strip()
            username = self.username_input.text().strip()
            password = self.password_input.text()
            service = self.service_input.text().strip()
            remember_me = self.remember_me_checkbox.isChecked()
            
            # Create connection worker
            from moodle_threads import ConnectionWorker
            from moodle_rest import MoodleRestClient
            
            try:
                client = MoodleRestClient(host, username, password, service)
                self.connection_worker = ConnectionWorker(client)
                
                # Connect signals
                self.connection_worker.signals.finished.connect(self.on_login_finished)
                self.connection_worker.signals.error.connect(self.on_login_error)
                self.connection_worker.signals.started.connect(self.on_login_started)
                
                # Start worker
                self.status_label.setText("Authenticating with Moodle...")
                self.connection_worker.start()
                
                logger.info(f"Connection test passed, proceeding with login for {username}@{host}")
                
            except Exception as e:
                self.on_login_error(f"Failed to initialize connection: {str(e)}")
        else:
            # Connection test failed
            self.status_label.setText("Connection test failed")
            self.status_label.setStyleSheet("color: #f44336;")
            self._add_diagnostics_message("FAILED: Connection test failed")
            
            # Show error details
            if test_result.get('error_log'):
                error_msg = test_result['error_log'][0] if test_result['error_log'] else "Unknown error"
                self._add_diagnostics_message(f"ERROR: {error_msg}")
                
                # Show recommendations
                if test_result.get('recommendations'):
                    self._add_diagnostics_message("\nRECOMMENDATIONS:")
                    for rec in test_result['recommendations']:
                        self._add_diagnostics_message(f"  - {rec}")
            
            self.set_ui_state(False)
            
            # Show error message to user
            error_msg = test_result.get('error_log', ['Connection test failed'])[0]
            QMessageBox.critical(self, "Connection Test Failed", 
                              f"Connection test failed:\n\n{error_msg}\n\nCheck the diagnostics for details.")
    
    def on_comprehensive_test_error(self, error_msg: str):
        """Handle comprehensive test error"""
        self.status_label.setText("Connection test error")
        self.status_label.setStyleSheet("color: #f44336;")
        self._add_diagnostics_message(f"TEST ERROR: {error_msg}")
        self.set_ui_state(False)
        
        QMessageBox.critical(self, "Test Error", f"Connection test encountered an error:\n\n{error_msg}")
    
    def test_connection(self):
        """Test connection without logging in"""
        if not self.validate_inputs():
            return
        
        # Get input values
        host = self.host_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        service = self.service_input.text().strip()
        
        # Show progress
        self.set_ui_state(True)
        self.status_label.setText("Testing connection...")
        self.status_label.setStyleSheet("color: #1976d2;")
        self.status_label.setVisible(True)
        self.diagnostics_button.setVisible(True)
        
        # Run test
        self.comprehensive_test_thread = ComprehensiveTestThread(
            self.connection_validator, host, username, password, service
        )
        self.comprehensive_test_thread.finished.connect(self.on_connection_test_finished)
        self.comprehensive_test_thread.error.connect(self.on_comprehensive_test_error)
        self.comprehensive_test_thread.progress.connect(self.on_test_progress)
        self.comprehensive_test_thread.start()
    
    def on_connection_test_finished(self, test_result: Dict[str, Any]):
        """Handle connection test completion"""
        self.set_ui_state(False)
        
        if test_result['success']:
            self.status_label.setText("Connection test successful")
            self.status_label.setStyleSheet("color: #4caf50;")
            self._add_diagnostics_message("SUCCESS: Connection test passed")
            
            QMessageBox.information(self, "Connection Test Successful", 
                                  "Connection test passed successfully!\n\nYou can now proceed with login.")
        else:
            self.status_label.setText("Connection test failed")
            self.status_label.setStyleSheet("color: #f44336;")
            self._add_diagnostics_message("FAILED: Connection test failed")
            
            # Show error details
            if test_result.get('error_log'):
                error_msg = test_result['error_log'][0] if test_result['error_log'] else "Unknown error"
                self._add_diagnostics_message(f"ERROR: {error_msg}")
                
                # Show recommendations
                if test_result.get('recommendations'):
                    self._add_diagnostics_message("\nRECOMMENDATIONS:")
                    for rec in test_result['recommendations']:
                        self._add_diagnostics_message(f"  - {rec}")
            
            QMessageBox.critical(self, "Connection Test Failed", 
                              f"Connection test failed:\n\n{test_result.get('error_log', ['Unknown error'])[0]}\n\nCheck the diagnostics for details.")
    
    def toggle_diagnostics(self, checked: bool):
        """Toggle diagnostics display"""
        self.diagnostics_text.setVisible(checked)
        if checked:
            self.diagnostics_button.setText("Hide Diagnostics")
            self._refresh_diagnostics()
        else:
            self.diagnostics_button.setText("Show Diagnostics")
    
    def _add_diagnostics_message(self, message: str):
        """Add a message to the diagnostics display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.diagnostics_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.diagnostics_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _refresh_diagnostics(self):
        """Refresh diagnostics display with current test results"""
        if hasattr(self.connection_validator, 'get_diagnostics_report'):
            report = self.connection_validator.get_diagnostics_report()
            self._add_diagnostics_message("=== DIAGNOSTICS REPORT ===")
            
            # Add test results
            for test_name, result in report.get('test_results', {}).items():
                status = "PASS" if result.get('success', False) else "FAIL"
                self._add_diagnostics_message(f"{test_name}: {status}")
                
                if not result.get('success', True) and result.get('error'):
                    self._add_diagnostics_message(f"  Error: {result['error']}")
            
            # Add error log
            if report.get('error_log'):
                self._add_diagnostics_message("\n=== ERROR LOG ===")
                for error in report['error_log']:
                    self._add_diagnostics_message(f"- {error}")
    
    def _validate_connection_params(self, host: str, username: str, password: str, service: str) -> bool:
        """Validate connection parameters"""
        valid, errors = self.connection_validator.validate_connection_parameters(host, username, password, service)
        
        if not valid:
            error_msg = "\n".join(errors)
            self._add_diagnostics_message(f"VALIDATION FAILED: {error_msg}")
            QMessageBox.critical(self, "Invalid Parameters", 
                              f"Please correct the following errors:\n\n{error_msg}")
            return False
        
        return True
    
    def on_login_started(self, message):
        """Handle login started signal"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #1976d2;")
    
    def on_login_finished(self, result):
        """Handle successful login"""
        try:
            # Show success message
            self.status_label.setText("Login successful! Preparing session...")
            self.status_label.setStyleSheet("color: #388e3c;")
            
            # Get connection details
            host = self.host_input.text().strip()
            username = self.username_input.text().strip()
            password = self.password_input.text()
            service = self.service_input.text().strip()
            remember_me = self.remember_me_checkbox.isChecked()
            
            # Validate the result
            if not result or not isinstance(result, dict):
                raise ValueError("Invalid login response from server")
            
            # Store credentials if remember me is checked
            if remember_me:
                self.status_label.setText("Securing your credentials...")
                success = self.auth_manager.store_credentials(host, username, password, service, remember_me)
                if success:
                    self.credentials_stored.emit(True)
                    logger.info("Credentials stored successfully")
                else:
                    self.credentials_stored.emit(False)
                    logger.warning("Failed to store credentials")
            
            # Create session
            self.status_label.setText("Creating secure session...")
            session_id = self.auth_manager.create_session(host, username, {
                'site_info': result,
                'service': service,
                'login_time': datetime.now().isoformat()
            })
            
            if not session_id:
                logger.warning("Failed to create session, but login was successful")
            
            # Emit success signal
            connection_details = {
                'host': host,
                'username': username,
                'service': service,
                'remember_me': remember_me,
                'site_info': result,
                'session_id': session_id
            }
            
            self.status_label.setText("Welcome! Loading your workspace...")
            self.login_successful.emit(connection_details)
            
            # Small delay for better UX
            QTimer.singleShot(500, self.accept)
            
            logger.info(f"Login successful for {username}@{host}")
            
        except Exception as e:
            logger.error(f"Error handling login success: {e}")
            self.on_login_error(f"Error processing login result: {e}")
    
    def on_login_error(self, error_message):
        """Handle login error with enhanced error handling"""
        # Hide progress
        self.set_ui_state(False)
        
        # Show error message
        self.status_label.setText("Login failed")
        self.status_label.setStyleSheet("color: #d32f2f;")
        
        # Enhanced error message with suggestions
        friendly_error = self._get_friendly_error_message(error_message)
        
        # Create detailed error dialog
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Login Failed")
        error_dialog.setText(friendly_error['title'])
        error_dialog.setInformativeText(friendly_error['message'])
        
        # Add detailed information
        if friendly_error.get('details'):
            error_dialog.setDetailedText(friendly_error['details'])
        
        # Add suggestions if available
        if friendly_error.get('suggestions'):
            suggestions = "\n\nSuggestions:\n" + "\n".join(f"• {s}" for s in friendly_error['suggestions'])
            error_dialog.setInformativeText(friendly_error['message'] + suggestions)
        
        error_dialog.exec_()
        
        # Emit error signal
        self.login_failed.emit(error_message)
        
        logger.error(f"Login failed: {error_message}")
    
    def _validate_connection_params(self, host: str, username: str, password: str, service: str) -> bool:
        """Validate connection parameters with detailed feedback"""
        errors = []
        
        # Validate host
        if not host or not host.strip():
            errors.append("Moodle URL is required")
        elif not (host.startswith('http://') or host.startswith('https://')):
            errors.append("Moodle URL must start with http:// or https://")
        elif len(host) < 8:
            errors.append("Moodle URL appears to be too short")
        
        # Validate username
        if not username or not username.strip():
            errors.append("Username is required")
        elif len(username) < 2:
            errors.append("Username must be at least 2 characters long")
        
        # Validate password
        if not password:
            errors.append("Password is required")
        elif len(password) < 1:
            errors.append("Password cannot be empty")
        
        # Validate service
        if not service or not service.strip():
            errors.append("Service name is required")
        
        if errors:
            error_msg = "\n".join(f"• {error}" for error in errors)
            QMessageBox.warning(self, "Validation Error", 
                              f"Please fix the following issues:\n\n{error_msg}")
            return False
        
        return True
    
    def _get_friendly_error_message(self, error_message: str) -> Dict[str, Any]:
        """Convert technical error messages to user-friendly ones with suggestions"""
        error_lower = error_message.lower()
        
        # Connection errors
        if any(keyword in error_lower for keyword in ['connection', 'network', 'timeout', 'unreachable']):
            return {
                'title': 'Connection Error',
                'message': 'Unable to connect to the Moodle server.',
                'details': error_message,
                'suggestions': [
                    'Check your internet connection',
                    'Verify the Moodle URL is correct',
                    'Ensure the Moodle server is running',
                    'Check if firewall is blocking the connection'
                ]
            }
        
        # Authentication errors
        elif any(keyword in error_lower for keyword in ['authentication', 'auth', 'login', 'invalid']):
            return {
                'title': 'Authentication Failed',
                'message': 'Invalid username or password.',
                'details': error_message,
                'suggestions': [
                    'Check your username and password',
                    'Ensure Caps Lock is off',
                    'Verify your account is active',
                    'Contact your administrator if you forgot your credentials'
                ]
            }
        
        # SSL/TLS errors
        elif any(keyword in error_lower for keyword in ['ssl', 'tls', 'certificate', 'security']):
            return {
                'title': 'Security Connection Error',
                'message': 'There is a problem with the secure connection.',
                'details': error_message,
                'suggestions': [
                    'The server SSL certificate may be invalid or expired',
                    'Try using https:// instead of http://',
                    'Contact your system administrator',
                    'Check if your system date and time are correct'
                ]
            }
        
        # Service/endpoint errors
        elif any(keyword in error_lower for keyword in ['service', 'endpoint', 'not found', '404']):
            return {
                'title': 'Service Configuration Error',
                'message': 'The Moodle web service is not properly configured.',
                'details': error_message,
                'suggestions': [
                    'Verify the service name is correct',
                    'Ensure Moodle web services are enabled',
                    'Check if the user has permission to access web services',
                    'Contact your Moodle administrator'
                ]
            }
        
        # Token errors
        elif any(keyword in error_lower for keyword in ['token', 'unauthorized', 'forbidden']):
            return {
                'title': 'Authorization Error',
                'message': 'Unable to obtain authorization token.',
                'details': error_message,
                'suggestions': [
                    'Verify your account has web service access',
                    'Check if the service is properly configured',
                    'Try logging out and back in',
                    'Contact your administrator'
                ]
            }
        
        # Generic error
        else:
            return {
                'title': 'Login Error',
                'message': 'An unexpected error occurred during login.',
                'details': error_message,
                'suggestions': [
                    'Try again in a few moments',
                    'Check your internet connection',
                    'Verify all login information is correct',
                    'Contact support if the problem persists'
                ]
            }
    
    def set_ui_state(self, busy: bool):
        """Set UI state (busy/ready)"""
        self.progress_bar.setVisible(busy)
        
        # Only enable credential inputs if not in MFA mode
        if not self.mfa_group.isVisible():
            self.host_input.setEnabled(not busy)
            self.service_input.setEnabled(not busy)
            self.username_input.setEnabled(not busy)
            self.password_input.setEnabled(not busy)
            self.remember_me_checkbox.setEnabled(not busy)
        
        # Handle MFA group state
        if self.mfa_group.isVisible():
            self.mfa_group.setEnabled(not busy)
        
        self.login_button.setEnabled(not busy)
        self.cancel_button.setEnabled(not busy)
        
        if busy:
            if self.mfa_group.isVisible():
                self.login_button.setText("Verifying...")
            else:
                self.login_button.setText("Connecting...")
        else:
            if self.mfa_group.isVisible():
                self.login_button.setText("Verify")
            else:
                self.login_button.setText("Login")
    
    def get_connection_details(self) -> Optional[Dict[str, Any]]:
        """Get connection details from the dialog"""
        if self.result() == QDialog.Accepted:
            return {
                'host': self.host_input.text().strip(),
                'username': self.username_input.text().strip(),
                'service': self.service_input.text().strip(),
                'remember_me': self.remember_me_checkbox.isChecked()
            }
        return None
    
    def clear_credentials(self):
        """Clear input fields"""
        self.host_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.service_input.setText("moodle_mobile_app")
        self.remember_me_checkbox.setChecked(False)
    
    def set_credentials(self, host: str, username: str, service: str = "moodle_mobile_app"):
        """Set credentials in the dialog"""
        self.host_input.setText(host)
        self.username_input.setText(username)
        self.service_input.setText(service)
        self.password_input.clear()
        self.password_input.setFocus()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


class ComprehensiveTestThread(QThread):
    """Thread for running comprehensive connection tests"""
    
    # Define signals as class attributes for PyQt5 compatibility
    finished = pyqtSignal(dict)  # Emits test result
    error = pyqtSignal(str)  # Emits error message
    progress = pyqtSignal(str)  # Emits progress updates
    
    def __init__(self, connection_validator: ConnectionValidator, host: str, username: str, password: str, service: str):
        super().__init__()
        self.connection_validator = connection_validator
        self.host = host
        self.username = username
        self.password = password
        self.service = service
        
    def run(self):
        """Run comprehensive connection tests"""
        try:
            self.progress.emit("Validating connection parameters...")
            
            # Validate parameters
            valid, errors = self.connection_validator.validate_connection_parameters(
                self.host, self.username, self.password, self.service
            )
            
            if not valid:
                result = {
                    'success': False,
                    'error_log': errors,
                    'recommendations': ['Please correct the parameter errors above']
                }
                self.finished.emit(result)
                return
            
            self.progress.emit("Testing network connectivity...")
            
            # Test network connectivity
            network_result = self.connection_validator.test_network_connectivity(self.host)
            if not network_result['success']:
                result = {
                    'success': False,
                    'error_log': network_result.get('error_log', ['Network connectivity test failed']),
                    'recommendations': network_result.get('recommendations', [])
                }
                self.finished.emit(result)
                return
            
            self.progress.emit("Testing Moodle service availability...")
            
            # Test Moodle service availability
            service_result = self.connection_validator.test_moodle_service(self.host)
            if not service_result['success']:
                result = {
                    'success': False,
                    'error_log': service_result.get('error_log', ['Moodle service test failed']),
                    'recommendations': service_result.get('recommendations', [])
                }
                self.finished.emit(result)
                return
            
            self.progress.emit("Testing authentication...")
            
            # Test authentication
            auth_result = self.connection_validator.test_authentication(
                self.host, self.username, self.password, self.service
            )
            
            if not auth_result['success']:
                result = {
                    'success': False,
                    'error_log': auth_result.get('error_log', ['Authentication test failed']),
                    'recommendations': auth_result.get('recommendations', [])
                }
                self.finished.emit(result)
                return
            
            # All tests passed
            result = {
                'success': True,
                'error_log': [],
                'recommendations': [],
                'test_results': {
                    'parameter_validation': {'success': True},
                    'network_connectivity': network_result,
                    'moodle_service': service_result,
                    'authentication': auth_result
                }
            }
            
            self.progress.emit("All tests completed successfully!")
            self.finished.emit(result)
            
        except Exception as e:
            error_msg = f"Comprehensive test error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)
