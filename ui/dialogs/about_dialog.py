"""
About Dialog for LMS Explorer
"""

import os
import sys


# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from utils.helpers.modern_styles import ModernStyles


class AboutDialog(QDialog):
    """About dialog for LMS Explorer"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("About LMS Explorer")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI with modern styling"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Apply modern styling to the dialog
        self.setStyleSheet(ModernStyles.get_group_box_style())
        
        # Title
        title_label = QLabel("LMS Explorer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(ModernStyles.get_label_style('title'))
        ModernStyles.apply_modern_font(title_label, 'title', True)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 2.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(ModernStyles.get_label_style('subtitle'))
        layout.addWidget(version_label)
        
        # Description
        description = QLabel(
            "A Learning Management System interface for Moodle.\n\n"
            "This application provides a user-friendly interface to browse and\n"
            "manage Moodle courses, users, and content."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet(ModernStyles.get_label_style('normal'))
        layout.addWidget(description)
        
        # Copyright
        copyright_label = QLabel("© 2025 Moodle Manager Team")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet(ModernStyles.get_label_style('muted'))
        layout.addWidget(copyright_label)
        
        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.setStyleSheet(ModernStyles.get_button_style('primary'))
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
