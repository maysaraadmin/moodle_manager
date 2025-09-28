"""
User Password Form for LMS Explorer
Dialog for managing user credentials
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon


class UserPasswordForm(QDialog):
    """
    Dialog form for managing user username and password
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._username = ""
        self._password = ""
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("User Credentials")
        self.setModal(True)
        self.resize(300, 150)
        
        # Center the dialog
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Username field
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.textChanged.connect(self._on_username_changed)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.textChanged.connect(self._on_password_changed)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def get_username(self) -> str:
        """Get the username"""
        return self._username
        
    def get_password(self) -> str:
        """Get the password"""
        return self._password
        
    def set_username(self, value: str):
        """Set the username"""
        self._username = value
        self.username_edit.setText(value)
        
    def set_password(self, value: str):
        """Set the password"""
        self._password = value
        self.password_edit.setText(value)
        
    def _on_username_changed(self, text: str):
        """Handle username text changed"""
        self._username = text
        
    def _on_password_changed(self, text: str):
        """Handle password text changed"""
        self._password = text
        
    # Properties for compatibility with Delphi interface
    username = property(get_username, set_username)
    password = property(get_password, set_password)
        
    def closeEvent(self, event):
        """Handle close event"""
        # Allow closing by default
        event.accept()
