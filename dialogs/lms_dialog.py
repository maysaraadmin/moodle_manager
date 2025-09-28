"""
LMS Connection Dialog
Dialog for connecting to LMS instances
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt


class LMSDialog(QDialog):
    """Dialog for connecting to LMS instances"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Connect to LMS")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        self.config_data = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # LMS Selection
        selection_layout = QHBoxLayout()
        selection_label = QLabel("LMS:")
        self.lms_combo = QComboBox()
        self.lms_combo.addItem("Select LMS...")
        self.lms_combo.currentIndexChanged.connect(self.on_lms_selected)
        
        selection_layout.addWidget(selection_label)
        selection_layout.addWidget(self.lms_combo)
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # Connection Details
        details_group = QVBoxLayout()
        
        # URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://your-moodle-site.com")
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_edit)
        details_group.addLayout(url_layout)
        
        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        details_group.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        details_group.addLayout(password_layout)
        
        # Service
        service_layout = QHBoxLayout()
        service_label = QLabel("Service:")
        self.service_edit = QLineEdit()
        self.service_edit.setText("moodle_mobile_app")
        
        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_edit)
        details_group.addLayout(service_layout)
        
        # Autoconnect
        self.autoconnect_checkbox = QCheckBox("Auto-connect on startup")
        details_group.addWidget(self.autoconnect_checkbox)
        
        # Remember me
        self.remember_me_checkbox = QCheckBox("Remember me (save password securely)")
        details_group.addWidget(self.remember_me_checkbox)
        
        layout.addLayout(details_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_lms)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def load_lms_configs(self, configs):
        """Load LMS configurations into the combo box"""
        self.lms_combo.clear()
        self.lms_combo.addItem("Select LMS...")
        
        for name, config in configs.items():
            self.lms_combo.addItem(name, config)
            
    def on_lms_selected(self, index):
        """Handle LMS selection change"""
        if index <= 0:
            # Clear fields
            self.url_edit.clear()
            self.username_edit.clear()
            self.password_edit.clear()
            self.service_edit.setText("moodle_mobile_app")
            self.autoconnect_checkbox.setChecked(False)
        else:
            # Load selected config
            config = self.lms_combo.currentData()
            if config:
                self.url_edit.setText(config.url)
                self.username_edit.setText(config.username)
                self.password_edit.setText(config.password)
                self.service_edit.setText(config.service)
                self.autoconnect_checkbox.setChecked(config.autoconnect)
                self.remember_me_checkbox.setChecked(config.remember_me)
                
    def test_connection(self):
        """Test the connection to the LMS"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return
            
        # Simple URL validation
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "Warning", "URL must start with http:// or https://")
            return
            
        # Test connection (placeholder implementation)
        # In a real implementation, this would use the MoodleRestClient
        try:
            import requests
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Connection test successful!")
            else:
                QMessageBox.warning(self, "Warning", f"Connection test failed: HTTP {response.status_code}")
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Connection test failed: {str(e)}")
            
    def connect_to_lms(self):
        """Connect to the selected LMS"""
        url = self.url_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        service = self.service_edit.text().strip()
        
        # Validation
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return
            
        if not username:
            QMessageBox.warning(self, "Warning", "Please enter a username")
            return
            
        if not password:
            QMessageBox.warning(self, "Warning", "Please enter a password")
            return
            
        if not service:
            QMessageBox.warning(self, "Warning", "Please enter a service name")
            return
            
        # Store connection data
        self.config_data = {
            'url': url,
            'username': username,
            'password': password,
            'service': service,
            'autoconnect': self.autoconnect_checkbox.isChecked(),
            'remember_me': self.remember_me_checkbox.isChecked()
        }
        
        # Accept the dialog
        self.accept()
        
    def get_connection_data(self):
        """Get the connection data"""
        return self.config_data
        
    def get_url(self):
        """Get the URL"""
        return self.config_data.get('url', '') if self.config_data else ''
        
    def get_username(self):
        """Get the username"""
        return self.config_data.get('username', '') if self.config_data else ''
        
    def get_password(self):
        """Get the password"""
        return self.config_data.get('password', '') if self.config_data else ''
        
    def get_service(self):
        """Get the service name"""
        return self.config_data.get('service', '') if self.config_data else ''
        
    def get_remember_me(self):
        """Get the remember me setting"""
        return self.config_data.get('remember_me', False) if self.config_data else False
