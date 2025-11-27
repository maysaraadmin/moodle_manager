#!/usr/bin/env python3
"""
Platform Manager Dialog for Moodle Manager
Handles adding, editing, and managing multiple Moodle platforms
"""

import os
import sys
from typing import Optional, Dict, Any

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QTextEdit, 
                             QCheckBox, QGroupBox, QMessageBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QSplitter, QWidget,
                             QTabWidget, QFormLayout, QSpinBox, QProgressBar,
                             QFrame, QStackedWidget, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QIcon, QFont, QPixmap

from core.data_models_multi import (MoodlePlatform, PlatformCredentials, 
                                   PlatformStatus, AuthType, MultiPlatformManager)
from utils.helpers.modern_styles import ModernStyles


class PlatformConnectionTestThread(QThread):
    """Thread for testing platform connections"""
    connection_result = pyqtSignal(str, bool, str)  # platform_id, success, message
    
    def __init__(self, platform: MoodlePlatform):
        super().__init__()
        self.platform = platform
    
    def run(self):
        """Test connection to platform"""
        try:
            # Simulate connection test
            # In real implementation, this would test actual Moodle API connection
            import time
            time.sleep(2)  # Simulate network delay
            
            # Mock successful connection for demo
            success = True
            message = "Connection successful" if success else "Connection failed"
            self.connection_result.emit(self.platform.id, success, message)
            
        except Exception as e:
            self.connection_result.emit(self.platform.id, False, str(e))


class PlatformEditDialog(QDialog):
    """Dialog for adding/editing a Moodle platform"""
    
    def __init__(self, platform: Optional[MoodlePlatform] = None, parent=None):
        super().__init__(parent)
        self.platform = platform
        self.is_edit_mode = platform is not None
        
        self.setWindowTitle("Edit Platform" if self.is_edit_mode else "Add New Platform")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        self.setup_ui()
        self.apply_styles()
        
        if self.is_edit_mode:
            self.load_platform_data()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content Widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(15, 15, 15, 15)
        scroll_area.setWidget(content_widget)
        
        main_layout.addWidget(scroll_area)
        
        # Basic Information
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(10)
        basic_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        basic_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., University Moodle")
        self.name_input.setMinimumHeight(35)
        basic_layout.addRow("Platform Name:", self.name_input)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("e.g., https://moodle.university.edu")
        self.url_input.setMinimumHeight(35)
        basic_layout.addRow("Moodle URL:", self.url_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        self.description_input.setPlaceholderText("Description of this Moodle platform...")
        basic_layout.addRow("Description:", self.description_input)
        
        content_layout.addWidget(basic_group)
        
        # Authentication Configuration
        auth_group = QGroupBox("Authentication Configuration")
        self.auth_layout = QFormLayout(auth_group)
        self.auth_layout.setSpacing(10)
        self.auth_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.auth_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.auth_type_combo = QComboBox()
        self.auth_type_combo.setMinimumHeight(35)
        auth_types = [
            ("Token", AuthType.TOKEN),
            ("Username/Password", AuthType.USERNAME_PASSWORD),
            ("OAuth2", AuthType.OAUTH2),
            ("API Key", AuthType.API_KEY)
        ]
        for display, value in auth_types:
            self.auth_type_combo.addItem(display, value)
        self.auth_type_combo.currentTextChanged.connect(self.on_auth_type_changed)
        self.auth_layout.addRow("Auth Type:", self.auth_type_combo)
        
        # Token input
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setPlaceholderText("Enter Moodle token...")
        self.token_input.setMinimumHeight(35)
        self.auth_layout.addRow("Token:", self.token_input)
        
        # Username/Password inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username...")
        self.username_input.setMinimumHeight(35)
        self.auth_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password...")
        self.password_input.setMinimumHeight(35)
        self.auth_layout.addRow("Password:", self.password_input)
        
        # API Key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter API key...")
        self.api_key_input.setMinimumHeight(35)
        self.auth_layout.addRow("API Key:", self.api_key_input)
        
        # OAuth2 inputs
        self.oauth_client_id_input = QLineEdit()
        self.oauth_client_id_input.setPlaceholderText("OAuth2 Client ID...")
        self.oauth_client_id_input.setMinimumHeight(35)
        self.auth_layout.addRow("Client ID:", self.oauth_client_id_input)
        
        self.oauth_client_secret_input = QLineEdit()
        self.oauth_client_secret_input.setEchoMode(QLineEdit.Password)
        self.oauth_client_secret_input.setPlaceholderText("OAuth2 Client Secret...")
        self.oauth_client_secret_input.setMinimumHeight(35)
        self.auth_layout.addRow("Client Secret:", self.oauth_client_secret_input)
        
        content_layout.addWidget(auth_group)
        
        # Advanced Settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout(advanced_group)
        advanced_layout.setSpacing(10)
        advanced_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        advanced_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.timezone_input = QLineEdit()
        self.timezone_input.setPlaceholderText("e.g., UTC, America/New_York")
        self.timezone_input.setMinimumHeight(35)
        advanced_layout.addRow("Timezone:", self.timezone_input)
        
        self.language_input = QLineEdit()
        self.language_input.setPlaceholderText("e.g., en")
        self.language_input.setMinimumHeight(35)
        advanced_layout.addRow("Language:", self.language_input)
        
        self.is_active_checkbox = QCheckBox("Platform is active")
        self.is_active_checkbox.setChecked(True)
        advanced_layout.addRow("", self.is_active_checkbox)
        
        content_layout.addWidget(advanced_group)
        
        # Test Connection Button
        self.test_connection_btn = QPushButton("Test Connection")
        self.test_connection_btn.setMinimumHeight(40)
        self.test_connection_btn.clicked.connect(self.test_connection)
        content_layout.addWidget(self.test_connection_btn)
        
        # Connection Status
        self.connection_status_label = QLabel("Not tested")
        self.connection_status_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.connection_status_label)
        
        content_layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.reject)
        
        btn_text = "Save Changes" if self.is_edit_mode else "Add Platform"
        self.save_button = QPushButton(btn_text)
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_platform)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        content_layout.addLayout(button_layout)
        
        # Initially hide all auth fields
        self.on_auth_type_changed()
    
    def apply_styles(self):
        """Apply modern styling"""
        self.setStyleSheet(ModernStyles.get_group_box_style())
        self.name_input.setStyleSheet(ModernStyles.get_input_style())
        self.url_input.setStyleSheet(ModernStyles.get_input_style())
        self.description_input.setStyleSheet(ModernStyles.get_input_style())
        self.auth_type_combo.setStyleSheet(ModernStyles.get_input_style())
        self.token_input.setStyleSheet(ModernStyles.get_input_style())
        self.username_input.setStyleSheet(ModernStyles.get_input_style())
        self.password_input.setStyleSheet(ModernStyles.get_input_style())
        self.api_key_input.setStyleSheet(ModernStyles.get_input_style())
        self.oauth_client_id_input.setStyleSheet(ModernStyles.get_input_style())
        self.oauth_client_secret_input.setStyleSheet(ModernStyles.get_input_style())
        self.timezone_input.setStyleSheet(ModernStyles.get_input_style())
        self.language_input.setStyleSheet(ModernStyles.get_input_style())
        self.test_connection_btn.setStyleSheet(ModernStyles.get_button_style('secondary'))
        self.save_button.setStyleSheet(ModernStyles.get_button_style('primary'))
        self.cancel_button.setStyleSheet(ModernStyles.get_button_style('outline'))
    
    def on_auth_type_changed(self):
        """Handle auth type change"""
        auth_type = self.auth_type_combo.currentData()
        
        # Helper to set row visibility
        def set_row_visible(widget, visible):
            widget.setVisible(visible)
            label = self.auth_layout.labelForField(widget)
            if label:
                label.setVisible(visible)
        
        # Hide all first
        set_row_visible(self.token_input, False)
        set_row_visible(self.username_input, False)
        set_row_visible(self.password_input, False)
        set_row_visible(self.api_key_input, False)
        set_row_visible(self.oauth_client_id_input, False)
        set_row_visible(self.oauth_client_secret_input, False)
        
        # Show relevant fields
        if auth_type == AuthType.TOKEN:
            set_row_visible(self.token_input, True)
        elif auth_type == AuthType.USERNAME_PASSWORD:
            set_row_visible(self.username_input, True)
            set_row_visible(self.password_input, True)
        elif auth_type == AuthType.API_KEY:
            set_row_visible(self.api_key_input, True)
        elif auth_type == AuthType.OAUTH2:
            set_row_visible(self.oauth_client_id_input, True)
            set_row_visible(self.oauth_client_secret_input, True)
    
    def load_platform_data(self):
        """Load platform data for editing"""
        if not self.platform:
            return
        
        self.name_input.setText(self.platform.name)
        self.url_input.setText(self.platform.url)
        self.description_input.setText(self.platform.description)
        
        # Set auth type and credentials
        auth_type = self.platform.credentials.auth_type
        index = self.auth_type_combo.findData(auth_type)
        if index >= 0:
            self.auth_type_combo.setCurrentIndex(index)
        
        self.token_input.setText(self.platform.credentials.token or "")
        self.username_input.setText(self.platform.credentials.username or "")
        self.password_input.setText(self.platform.credentials.password or "")
        self.api_key_input.setText(self.platform.credentials.api_key or "")
        self.oauth_client_id_input.setText(self.platform.credentials.oauth_client_id or "")
        self.oauth_client_secret_input.setText(self.platform.credentials.oauth_client_secret or "")
        
        self.timezone_input.setText(self.platform.timezone or "")
        self.language_input.setText(self.platform.language or "")
        self.is_active_checkbox.setChecked(self.platform.is_active)
    
    def test_connection(self):
        """Test connection to the platform"""
        # Validate inputs
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter a platform name.")
            return
        
        if not self.url_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter a Moodle URL.")
            return
        
        # Create temporary platform for testing
        platform = self.create_platform_object()
        
        # Start connection test
        self.test_connection_btn.setEnabled(False)
        self.test_connection_btn.setText("Testing...")
        self.connection_status_label.setText("Testing connection...")
        self.connection_status_label.setStyleSheet(ModernStyles.get_label_style('normal'))
        
        self.test_thread = PlatformConnectionTestThread(platform)
        self.test_thread.connection_result.connect(self.on_connection_test_result)
        self.test_thread.start()
    
    def on_connection_test_result(self, platform_id: str, success: bool, message: str):
        """Handle connection test result"""
        self.test_connection_btn.setEnabled(True)
        self.test_connection_btn.setText("Test Connection")
        
        if success:
            self.connection_status_label.setText("✅ Connection successful")
            self.connection_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.connection_status_label.setText(f"❌ Connection failed: {message}")
            self.connection_status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
    
    def create_platform_object(self) -> MoodlePlatform:
        """Create platform object from form data"""
        auth_type = self.auth_type_combo.currentData()
        
        credentials = PlatformCredentials(
            auth_type=auth_type,
            token=self.token_input.text().strip() or None,
            username=self.username_input.text().strip() or None,
            password=self.password_input.text().strip() or None,
            api_key=self.api_key_input.text().strip() or None,
            oauth_client_id=self.oauth_client_id_input.text().strip() or None,
            oauth_client_secret=self.oauth_client_secret_input.text().strip() or None
        )
        
        import uuid
        platform_id = self.platform.id if self.platform else str(uuid.uuid4())
        
        return MoodlePlatform(
            id=platform_id,
            name=self.name_input.text().strip(),
            url=self.url_input.text().strip(),
            description=self.description_input.toPlainText().strip(),
            credentials=credentials,
            timezone=self.timezone_input.text().strip() or None,
            language=self.language_input.text().strip() or None,
            is_active=self.is_active_checkbox.isChecked()
        )
    
    def save_platform(self):
        """Save the platform"""
        try:
            platform = self.create_platform_object()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving platform: {str(e)}")
    
    def get_platform(self) -> MoodlePlatform:
        """Get the created/edited platform"""
        return self.create_platform_object()


class PlatformManagerDialog(QDialog):
    """Main platform management dialog"""
    
    platform_selected = pyqtSignal(str)  # platform_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.multi_platform_manager = MultiPlatformManager()
        
        self.setWindowTitle("Moodle Platform Manager")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        self.setup_ui()
        self.apply_styles()
        self.load_platforms()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("Moodle Platform Manager")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet(ModernStyles.get_label_style('title'))
        ModernStyles.apply_modern_font(header_label, 'title', True)
        layout.addWidget(header_label)
        
        # Stats Bar
        self.create_stats_bar(layout)
        
        # Main Content (Splitter)
        splitter = QSplitter(Qt.Horizontal)
        
        # Platform List
        self.create_platform_list(splitter)
        
        # Platform Details
        self.create_platform_details(splitter)
        
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        # Action Buttons
        self.create_action_buttons(layout)
        
        # Status Bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(ModernStyles.get_label_style('muted'))
        layout.addWidget(self.status_label)
    
    def create_stats_bar(self, parent_layout):
        """Create statistics bar"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet(ModernStyles.get_frame_style())
        stats_layout = QHBoxLayout(stats_frame)
        
        self.total_platforms_label = QLabel("Total: 0")
        self.active_platforms_label = QLabel("Active: 0")
        self.connected_platforms_label = QLabel("Connected: 0")
        self.sessions_label = QLabel("Sessions: 0")
        
        stats_layout.addWidget(self.total_platforms_label)
        stats_layout.addWidget(QLabel("|"))
        stats_layout.addWidget(self.active_platforms_label)
        stats_layout.addWidget(QLabel("|"))
        stats_layout.addWidget(self.connected_platforms_label)
        stats_layout.addWidget(QLabel("|"))
        stats_layout.addWidget(self.sessions_label)
        stats_layout.addStretch()
        
        parent_layout.addWidget(stats_frame)
    
    def create_platform_list(self, parent):
        """Create platform list widget"""
        list_frame = QFrame()
        list_layout = QVBoxLayout(list_frame)
        
        # List Header
        list_header = QLabel("Platforms")
        list_header.setStyleSheet(ModernStyles.get_label_style('subtitle'))
        ModernStyles.apply_modern_font(list_header, 'subtitle', True)
        list_layout.addWidget(list_header)
        
        # Platform Table
        self.platform_table = QTableWidget()
        self.platform_table.setColumnCount(5)
        self.platform_table.setHorizontalHeaderLabels(["Name", "URL", "Status", "Auth Type", "Active"])
        self.platform_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.platform_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.platform_table.itemSelectionChanged.connect(self.on_platform_selection_changed)
        self.platform_table.itemDoubleClicked.connect(self.on_edit_platform)
        
        list_layout.addWidget(self.platform_table)
        parent.addWidget(list_frame)
    
    def create_platform_details(self, parent):
        """Create platform details panel"""
        details_frame = QFrame()
        details_layout = QVBoxLayout(details_frame)
        
        # Details Header
        details_header = QLabel("Platform Details")
        details_header.setStyleSheet(ModernStyles.get_label_style('subtitle'))
        ModernStyles.apply_modern_font(details_header, 'subtitle', True)
        details_layout.addWidget(details_header)
        
        # Details Content
        self.details_stack = QStackedWidget()
        
        # Empty state
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_label = QLabel("Select a platform to view details")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet(ModernStyles.get_label_style('muted'))
        empty_layout.addWidget(empty_label)
        self.details_stack.addWidget(empty_widget)
        
        # Platform details widget
        self.details_widget = QWidget()
        details_form = QFormLayout(self.details_widget)
        
        self.detail_name_label = QLabel()
        self.detail_url_label = QLabel()
        self.detail_description_label = QLabel()
        self.detail_status_label = QLabel()
        self.detail_auth_type_label = QLabel()
        self.detail_created_label = QLabel()
        self.detail_last_connected_label = QLabel()
        self.detail_connection_count_label = QLabel()
        self.detail_timezone_label = QLabel()
        self.detail_language_label = QLabel()
        
        details_form.addRow("Name:", self.detail_name_label)
        details_form.addRow("URL:", self.detail_url_label)
        details_form.addRow("Description:", self.detail_description_label)
        details_form.addRow("Status:", self.detail_status_label)
        details_form.addRow("Auth Type:", self.detail_auth_type_label)
        details_form.addRow("Created:", self.detail_created_label)
        details_form.addRow("Last Connected:", self.detail_last_connected_label)
        details_form.addRow("Connection Count:", self.detail_connection_count_label)
        details_form.addRow("Timezone:", self.detail_timezone_label)
        details_form.addRow("Language:", self.detail_language_label)
        
        self.details_stack.addWidget(self.details_widget)
        
        details_layout.addWidget(self.details_stack)
        parent.addWidget(details_frame)
    
    def create_action_buttons(self, parent_layout):
        """Create action buttons"""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        self.add_button = QPushButton("Add Platform")
        self.add_button.clicked.connect(self.on_add_platform)
        
        self.edit_button = QPushButton("Edit Platform")
        self.edit_button.clicked.connect(self.on_edit_platform)
        self.edit_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete Platform")
        self.delete_button.clicked.connect(self.on_delete_platform)
        self.delete_button.setEnabled(False)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.on_connect_platform)
        self.connect_button.setEnabled(False)
        
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.on_disconnect_platform)
        self.disconnect_button.setEnabled(False)
        
        self.switch_button = QPushButton("Switch to Platform")
        self.switch_button.clicked.connect(self.on_switch_to_platform)
        self.switch_button.setEnabled(False)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)
        button_layout.addStretch()
        button_layout.addWidget(self.switch_button)
        
        parent_layout.addWidget(button_frame)
    
    def apply_styles(self):
        """Apply modern styling"""
        self.setStyleSheet(ModernStyles.get_group_box_style())
        self.platform_table.setStyleSheet(ModernStyles.get_tree_style())
        self.add_button.setStyleSheet(ModernStyles.get_button_style('success'))
        self.edit_button.setStyleSheet(ModernStyles.get_button_style('primary'))
        self.delete_button.setStyleSheet(ModernStyles.get_button_style('danger'))
        self.connect_button.setStyleSheet(ModernStyles.get_button_style('primary'))
        self.disconnect_button.setStyleSheet(ModernStyles.get_button_style('secondary'))
        self.switch_button.setStyleSheet(ModernStyles.get_button_style('success'))
    
    def load_platforms(self):
        """Load platforms into the table"""
        platforms = self.multi_platform_manager.get_all_platforms()
        self.platform_table.setRowCount(len(platforms))
        
        for row, platform in enumerate(platforms):
            self.platform_table.setItem(row, 0, QTableWidgetItem(platform.name))
            self.platform_table.setItem(row, 1, QTableWidgetItem(platform.url))
            self.platform_table.setItem(row, 2, QTableWidgetItem(platform.status.value))
            self.platform_table.setItem(row, 3, QTableWidgetItem(platform.credentials.auth_type.value))
            self.platform_table.setItem(row, 4, QTableWidgetItem("Yes" if platform.is_active else "No"))
        
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        stats = self.multi_platform_manager.get_platform_stats()
        self.total_platforms_label.setText(f"Total: {stats['total_platforms']}")
        self.active_platforms_label.setText(f"Active: {stats['active_platforms']}")
        self.connected_platforms_label.setText(f"Connected: {stats['connected_platforms']}")
        self.sessions_label.setText(f"Sessions: {stats['total_sessions']}")
    
    def on_platform_selection_changed(self):
        """Handle platform selection change"""
        selected_rows = self.platform_table.selectedItems()
        has_selection = len(selected_rows) > 0
        
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.connect_button.setEnabled(has_selection)
        self.disconnect_button.setEnabled(has_selection)
        self.switch_button.setEnabled(has_selection)
        
        if has_selection:
            row = selected_rows[0].row()
            platforms = self.multi_platform_manager.get_all_platforms()
            if row < len(platforms):
                platform = platforms[row]
                self.show_platform_details(platform)
        else:
            self.details_stack.setCurrentIndex(0)
    
    def show_platform_details(self, platform: MoodlePlatform):
        """Show platform details"""
        self.detail_name_label.setText(platform.name)
        self.detail_url_label.setText(platform.url)
        self.detail_description_label.setText(platform.description or "N/A")
        self.detail_status_label.setText(platform.status.value)
        self.detail_auth_type_label.setText(platform.credentials.auth_type.value)
        self.detail_created_label.setText(platform.created_at.strftime("%Y-%m-%d %H:%M"))
        self.detail_last_connected_label.setText(
            platform.last_connected.strftime("%Y-%m-%d %H:%M") if platform.last_connected else "Never"
        )
        self.detail_connection_count_label.setText(str(platform.connection_count))
        self.detail_timezone_label.setText(platform.timezone or "N/A")
        self.detail_language_label.setText(platform.language or "N/A")
        
        self.details_stack.setCurrentIndex(1)
    
    def on_add_platform(self):
        """Handle add platform"""
        dialog = PlatformEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            platform = dialog.get_platform()
            self.multi_platform_manager.add_platform(platform)
            self.load_platforms()
            self.status_label.setText(f"Added platform: {platform.name}")
    
    def on_edit_platform(self):
        """Handle edit platform"""
        selected_rows = self.platform_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        platforms = self.multi_platform_manager.get_all_platforms()
        if row < len(platforms):
            platform = platforms[row]
            dialog = PlatformEditDialog(platform, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                updated_platform = dialog.get_platform()
                self.multi_platform_manager.platforms[updated_platform.id] = updated_platform
                self.multi_platform_manager.save_config()
                self.load_platforms()
                self.status_label.setText(f"Updated platform: {updated_platform.name}")
    
    def on_delete_platform(self):
        """Handle delete platform"""
        selected_rows = self.platform_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        platforms = self.multi_platform_manager.get_all_platforms()
        if row < len(platforms):
            platform = platforms[row]
            
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete platform '{platform.name}'?\n\n"
                "This will also remove all associated sessions.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.multi_platform_manager.remove_platform(platform.id):
                    self.load_platforms()
                    self.status_label.setText(f"Deleted platform: {platform.name}")
    
    def on_connect_platform(self):
        """Handle connect platform"""
        selected_rows = self.platform_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        platforms = self.multi_platform_manager.get_all_platforms()
        if row < len(platforms):
            platform = platforms[row]
            self.multi_platform_manager.update_platform_status(platform.id, PlatformStatus.CONNECTING)
            self.load_platforms()
            
            # Simulate connection
            QTimer.singleShot(2000, lambda: self.complete_connection(platform.id))
            self.status_label.setText(f"Connecting to {platform.name}...")
    
    def complete_connection(self, platform_id: str):
        """Complete platform connection"""
        self.multi_platform_manager.update_platform_status(platform_id, PlatformStatus.CONNECTED)
        self.load_platforms()
        
        platform = self.multi_platform_manager.get_platform(platform_id)
        if platform:
            self.status_label.setText(f"Connected to {platform.name}")
    
    def on_disconnect_platform(self):
        """Handle disconnect platform"""
        selected_rows = self.platform_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        platforms = self.multi_platform_manager.get_all_platforms()
        if row < len(platforms):
            platform = platforms[row]
            self.multi_platform_manager.update_platform_status(platform.id, PlatformStatus.DISCONNECTED)
            self.load_platforms()
            self.status_label.setText(f"Disconnected from {platform.name}")
    
    def on_switch_to_platform(self):
        """Handle switch to platform"""
        selected_rows = self.platform_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        platforms = self.multi_platform_manager.get_all_platforms()
        if row < len(platforms):
            platform = platforms[row]
            if self.multi_platform_manager.set_active_platform(platform.id):
                self.platform_selected.emit(platform.id)
                self.accept()
                self.status_label.setText(f"Switched to platform: {platform.name}")
    
    def get_selected_platform(self) -> Optional[MoodlePlatform]:
        """Get the currently selected platform"""
        selected_rows = self.platform_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        platforms = self.multi_platform_manager.get_all_platforms()
        if row < len(platforms):
            return platforms[row]
        return None
