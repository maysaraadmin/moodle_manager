"""
Main Window for LMS Explorer
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QMenuBar, QMenu, QAction, QStatusBar, QSplitter,
                             QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
                             QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from data_models import LMS
from config_manager import ConfigManager, LMSConfig
from tree_views.network_tree import NetworkTreeWidget
from dialogs.about_dialog import AboutDialog
from dialogs.lms_dialog import LMSDialog


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.lms_interface = LMS()
        self.config_manager = ConfigManager()
        
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("LMS Explorer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Create left panel (tree view)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Filter input
        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter...")
        self.filter_edit.textChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_edit)
        
        # Tree view buttons
        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self.on_collapse_all)
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self.on_expand_all)
        
        filter_layout.addWidget(self.collapse_all_btn)
        filter_layout.addWidget(self.expand_all_btn)
        left_layout.addLayout(filter_layout)
        
        # Network tree widget
        self.network_tree = NetworkTreeWidget()
        left_layout.addWidget(self.network_tree)
        
        # Create right panel (content area)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Content area (placeholder for now)
        self.content_area = QTreeWidget()
        self.content_area.setHeaderLabels(["Content"])
        right_layout.addWidget(self.content_area)
        
        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 800])
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # LMS menu
        lms_menu = menubar.addMenu("LMS")
        
        # Connect action
        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self.on_connect)
        lms_menu.addAction(connect_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = self.addToolBar("Main Toolbar")
        
        # Connect action
        connect_action = QAction("Connect", self)
        connect_action.setStatusTip("Connect to LMS")
        connect_action.triggered.connect(self.on_connect)
        toolbar.addAction(connect_action)
        
        toolbar.addSeparator()
        
        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.setStatusTip("Refresh data from LMS")
        refresh_action.triggered.connect(self.on_refresh)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # About action
        about_action = QAction("About", self)
        about_action.setStatusTip("About LMS Explorer")
        about_action.triggered.connect(self.on_about)
        toolbar.addAction(about_action)
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        toolbar.addAction(exit_action)
        
    def load_config(self):
        """Load configuration from config file"""
        config_path = os.path.join(os.path.dirname(sys.executable), 'config.ini')
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
            
        if os.path.exists(config_path):
            self.config_manager.load_config(config_path)
            self.status_bar.showMessage(f"Configuration loaded from {config_path}")
            
            # Check for auto-connect configuration
            autoconnect_config = self.config_manager.get_autoconnect_config()
            if autoconnect_config:
                # Auto-connect to the configured LMS
                self.auto_connect_to_lms(autoconnect_config)
        else:
            self.status_bar.showMessage("No configuration file found")
            
    def on_filter_changed(self, text):
        """Handle filter text change"""
        # Filter the tree view based on the text
        self.network_tree.filter_items(text)
        
    def on_collapse_all(self):
        """Collapse all tree items"""
        self.network_tree.collapseAll()
        
    def on_expand_all(self):
        """Expand all tree items"""
        self.network_tree.expandAll()
        
    def on_connect(self):
        """Handle connect action"""
        dialog = LMSDialog(self)
        
        # Load existing configurations into the dialog
        configs = self.config_manager.get_all_configs()
        dialog.load_lms_configs(configs)
        
        if dialog.exec_():
            # Get connection details from dialog
            url = dialog.get_url()
            username = dialog.get_username()
            password = dialog.get_password()
            service = dialog.get_service()
            remember_me = dialog.get_remember_me()
            autoconnect = dialog.get_connection_data().get('autoconnect', False)
            
            # Set LMS details
            self.lms_interface.set_host(url)
            self.lms_interface.set_name("Moodle")
            
            # Connect to LMS
            self.status_bar.showMessage("Connecting to LMS...")
            
            if self.lms_interface.connect(username, password, service):
                self.status_bar.showMessage("Connected to LMS")
                
                # Update the network tree with loaded data
                self.network_tree.set_lms(self.lms_interface)
                
                # Save configuration
                self.config_manager.add_config(
                    name="Moodle",
                    url=url,
                    username=username,
                    password=password,
                    service=service,
                    autoconnect=autoconnect,
                    remember_me=remember_me
                )
                self.config_manager.save_config()
                
                print(f"Successfully connected and loaded {len(self.lms_interface.get_categories())} categories and {len(self.lms_interface.get_courses())} courses")
            else:
                self.status_bar.showMessage("Connection failed")
                print("Failed to connect to LMS")
            
    def auto_connect_to_lms(self, config):
        """Auto-connect to LMS using the provided configuration"""
        self.status_bar.showMessage(f"Auto-connecting to {config.name}...")
        
        # Set LMS details
        self.lms_interface.set_host(config.url)
        self.lms_interface.set_name(config.name)
        
        # Connect to LMS
        if self.lms_interface.connect(config.username, config.password, config.service):
            self.status_bar.showMessage(f"Auto-connected to {config.name}")
            
            # Update the network tree with loaded data
            self.network_tree.set_lms(self.lms_interface)
            
            print(f"Auto-connected successfully and loaded {len(self.lms_interface.get_categories())} categories and {len(self.lms_interface.get_courses())} courses")
        else:
            self.status_bar.showMessage(f"Auto-connect failed for {config.name}")
            print(f"Failed to auto-connect to {config.name}")
    
    def on_about(self):
        """Handle about action"""
        dialog = AboutDialog(self)
        dialog.exec_()
        
    def on_refresh(self):
        """Handle refresh action"""
        if self.lms_interface and self.lms_interface.is_connected():
            self.status_bar.showMessage("Refreshing data from LMS...")
            # Refresh the network tree
            self.network_tree.refresh_data()
            self.status_bar.showMessage("Data refreshed successfully")
        else:
            self.status_bar.showMessage("Not connected to LMS")
            QMessageBox.warning(self, "Not Connected", "Please connect to LMS first.")
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save configuration if needed
        event.accept()
