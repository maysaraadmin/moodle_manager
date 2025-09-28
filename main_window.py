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
        # This would be implemented with actual toolbar actions
        pass
        
    def load_config(self):
        """Load configuration from config file"""
        config_path = os.path.join(os.path.dirname(sys.executable), 'config.ini')
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
            
        if os.path.exists(config_path):
            self.config_manager.load_config(config_path)
            self.status_bar.showMessage(f"Configuration loaded from {config_path}")
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
        if dialog.exec_():
            # Get connection details from dialog
            url = dialog.get_url()
            username = dialog.get_username()
            password = dialog.get_password()
            service = dialog.get_service()
            
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
                    autoconnect=False
                )
                self.config_manager.save_config()
                
                print(f"Successfully connected and loaded {len(self.lms_interface.get_categories())} categories and {len(self.lms_interface.get_courses())} courses")
            else:
                self.status_bar.showMessage("Connection failed")
                print("Failed to connect to LMS")
            
    def on_about(self):
        """Handle about action"""
        dialog = AboutDialog(self)
        dialog.exec_()
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save configuration if needed
        event.accept()
