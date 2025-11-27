#!/usr/bin/env python3
"""
Moodle Information Page for Moodle Manager
Simple page to display Moodle platform information
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import sys
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QMessageBox, QFrame,
                             QScrollArea, QTextEdit, QGridLayout, QFormLayout,
                             QProgressBar, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QIcon, QFont, QPalette, QPixmap

from core.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class MoodleInfoPage(QWidget):
    """Simple page to display Moodle platform information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_manager = DatabaseManager()
        self.setup_ui()
        self.load_moodle_info()
        
    def setup_ui(self):
        """Setup the Moodle information page UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        self.create_header(main_layout)
        
        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Info sections
        self.create_about_section(content_layout)
        self.create_features_section(content_layout)
        self.create_servers_section(content_layout)
        self.create_connection_section(content_layout)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Apply styling
        self.apply_modern_style()
        
    def create_header(self, parent_layout):
        """Create page header"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel("Moodle Platform Information")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px 0;")
        
        # Subtitle
        subtitle_label = QLabel("Connect to your Moodle Learning Management System")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        parent_layout.addWidget(header_frame)
        
    def create_about_section(self, parent_layout):
        """Create about Moodle section"""
        about_group = QGroupBox("About Moodle")
        about_group.setFont(QFont("Arial", 12, QFont.Bold))
        about_layout = QVBoxLayout(about_group)
        
        # About text
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setMaximumHeight(120)
        about_text.setHtml("""
        <p><strong>Moodle</strong> is the world's most popular learning management system (LMS) 
        used by millions of educators, students and administrators worldwide.</p>
        
        <p>With Moodle, you can create and manage online learning environments, 
        deliver courses, and track student progress in a flexible, feature-rich platform.</p>
        
        <p><strong>Key Features:</strong> Course management, user authentication, 
        collaborative tools, assessments, and much more.</p>
        """)
        about_layout.addWidget(about_text)
        
        parent_layout.addWidget(about_group)
        
    def create_features_section(self, parent_layout):
        """Create features section"""
        features_group = QGroupBox("Platform Features")
        features_group.setFont(QFont("Arial", 12, QFont.Bold))
        features_layout = QGridLayout(features_group)
        
        # Feature list
        features = [
            ("📚", "Course Management", "Create and organize courses with rich content"),
            ("👥", "User Management", "Manage students, teachers, and administrators"),
            ("📝", "Assignments & Quizzes", "Create assessments with various question types"),
            ("💬", "Communication", "Forums, messaging, and collaboration tools"),
            ("📊", "Analytics", "Track progress and generate reports"),
            ("🔧", "Customization", "Extensible with plugins and themes"),
            ("📱", "Mobile Access", "Mobile app for learning on the go"),
            ("🔒", "Security", "Robust authentication and data protection")
        ]
        
        for i, (icon, title, description) in enumerate(features):
            row = i // 2
            col = (i % 2) * 2
            
            # Icon
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 16))
            icon_label.setAlignment(Qt.AlignCenter)
            features_layout.addWidget(icon_label, row, col)
            
            # Title and description
            title_label = QLabel(f"<strong>{title}</strong>")
            title_label.setWordWrap(True)
            features_layout.addWidget(title_label, row, col + 1)
            
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #6c757d; font-size: 9pt;")
            features_layout.addWidget(desc_label, row + 1, col + 1)
            
            if col == 0:  # Add spacing between columns
                features_layout.setColumnStretch(col, 1)
                features_layout.setColumnStretch(col + 1, 2)
        
        parent_layout.addWidget(features_group)
        
    def create_servers_section(self, parent_layout):
        """Create saved servers section"""
        servers_group = QGroupBox("Saved Moodle Servers")
        servers_group.setFont(QFont("Arial", 12, QFont.Bold))
        servers_layout = QVBoxLayout(servers_group)
        
        # Load servers from database
        servers = self.database_manager.get_all_moodle_servers()
        
        if servers:
            for server in servers:
                server_frame = QFrame()
                server_frame.setFrameStyle(QFrame.Box)
                server_layout = QHBoxLayout(server_frame)
                
                # Server info
                info_layout = QVBoxLayout()
                
                host_label = QLabel(f"<strong>{server['host']}</strong>")
                host_label.setFont(QFont("Arial", 10, QFont.Bold))
                
                username_label = QLabel(f"Username: {server.get('username', 'N/A')}")
                username_label.setStyleSheet("color: #6c757d;")
                
                # Service info
                service_label = QLabel(f"Service: {server.get('service', 'moodle_mobile_app')}")
                service_label.setStyleSheet("color: #6c757d; font-size: 9pt;")
                
                info_layout.addWidget(host_label)
                info_layout.addWidget(username_label)
                info_layout.addWidget(service_label)
                
                # Status indicator
                status_label = QLabel("💾 Saved")
                status_label.setStyleSheet("color: #28a745; font-weight: bold;")
                
                server_layout.addLayout(info_layout)
                server_layout.addStretch()
                server_layout.addWidget(status_label)
                
                servers_layout.addWidget(server_frame)
        else:
            no_servers_label = QLabel("No Moodle servers saved yet. Connect to a server to get started.")
            no_servers_label.setAlignment(Qt.AlignCenter)
            no_servers_label.setStyleSheet("color: #6c757d; font-style: italic; padding: 20px;")
            servers_layout.addWidget(no_servers_label)
            
        parent_layout.addWidget(servers_group)
        
    def create_connection_section(self, parent_layout):
        """Create connection section"""
        connection_group = QGroupBox("Connection Options")
        connection_group.setFont(QFont("Arial", 12, QFont.Bold))
        connection_layout = QVBoxLayout(connection_group)
        
        # Connection info
        info_label = QLabel("Moodle connection features have been disabled.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #495057; margin-bottom: 15px;")
        connection_layout.addWidget(info_label)
        
        # Help text
        help_label = QLabel("Contact your administrator if you need to enable Moodle connections.")
        help_label.setAlignment(Qt.AlignCenter)
        help_label.setStyleSheet("color: #6c757d; font-size: 9pt; margin-top: 10px;")
        connection_layout.addWidget(help_label)
        
        parent_layout.addWidget(connection_group)
        
    def load_moodle_info(self):
        """Load Moodle information from database"""
        try:
            # Get server count
            servers = self.database_manager.get_all_moodle_servers()
            server_count = len(servers)
            
        except Exception as e:
            logger.error(f"Error loading Moodle info: {e}")
            
    def apply_modern_style(self):
        """Apply modern styling to the page"""
        self.setStyleSheet("""
            QWidget {
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
            
            QTextEdit {
                border: none;
                background-color: transparent;
                color: #495057;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QFrame[frameShape="5"] {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: #f8f9fa;
                padding: 10px;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
