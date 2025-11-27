"""
Main Window for LMS Explorer
Enhanced UI with modern styling and improved functionality
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import webbrowser
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QMenuBar, QMenu, QAction, QStatusBar, QSplitter,
                             QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
                             QMessageBox, QFileDialog, QProgressBar, QLabel,
                             QFrame, QSizePolicy, QHeaderView, QStackedWidget, QTextBrowser,
                             QComboBox, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPalette

from core.data_models import LMS
from utils.config.config_manager import ConfigManager, LMSConfig
from ui.views.network_tree import NetworkTreeWidget
from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.lms_dialog import LMSDialog
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.login_dialog import LoginDialog
from core.auth.auth_manager import AuthManager
from core.database.database_manager import DatabaseManager
from core.auth.user_session_manager import UserSessionManager
from ui.dialogs.user_profile_dialog import UserProfileDialog
from core.system.system_user_manager import SystemUserManager
from core.system.system_profile_dialog import SystemProfileDialog
from ui.main.moodle_info_page import MoodleInfoPage
from ui.dialogs.platform_manager_dialog import PlatformManagerDialog
from utils.helpers.modern_styles import ModernStyles
from core.data_models_multi import MultiPlatformManager



# Configure logging
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.lms_interface = LMS()
        self.config_manager = ConfigManager()
        self.auth_manager = AuthManager("MoodleManager")
        self.database_manager = DatabaseManager()
        self.session_manager = UserSessionManager("MoodleManager")
        self.system_user_manager = SystemUserManager()
        
        # Multi-platform manager
        self.multi_platform_manager = MultiPlatformManager()
        
        # System user data
        self.system_user = None
        self.system_session_token = None
        
        self.init_ui()
        self.load_config()
        self.setup_platform_ui()
        
    def set_system_user(self, user_data, session_token):
        """Set system user data and session token"""
        try:
            self.system_user = user_data
            self.system_session_token = session_token
            
            # Update window title with username
            username = user_data.get('username', 'Unknown')
            self.setWindowTitle(f"LMS Explorer - {username}")
            
            # Update status bar
            full_name = user_data.get('full_name', username)
            self.statusBar().showMessage(f"Logged in as: {full_name}")
            
            print(f"System user set: {username}")
        except Exception as e:
            print(f"Error setting system user: {e}")
            raise
        
    def init_ui(self):
        """Initialize the user interface with modern styling"""
        self.setWindowTitle("LMS Explorer - Learning Management System")
        self.setGeometry(100, 100, 1400, 900)

        # Set application icon if available
        self.setWindowIcon(self.style().standardIcon(self.style().SP_ComputerIcon))

        # Apply modern styling
        self.apply_modern_style()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create menu bar
        self.create_menu_bar()

        # Create enhanced toolbar
        self.create_enhanced_toolbar()

        # Create main content area
        self.create_main_content_area(main_layout)

        # Create enhanced status bar
        self.create_enhanced_status_bar()

    def create_enhanced_toolbar(self):
        """Create the enhanced toolbar with better styling and more actions"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)

        toolbar.addSeparator()

        # Data management section
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.setStatusTip("Refresh data from LMS")
        refresh_action.setToolTip("Refresh all data from connected LMS")
        refresh_action.triggered.connect(self.on_refresh)
        toolbar.addAction(refresh_action)

        # Export action
        export_action = QAction("📊 Export", self)
        export_action.setStatusTip("Export data to file")
        export_action.setToolTip("Export courses and users to Excel/CSV")
        export_action.triggered.connect(self.on_export)
        toolbar.addAction(export_action)

        toolbar.addSeparator()

        # Multi-platform section
        # Add Platform action
        add_platform_action = QAction("➕ Add Platform", self)
        add_platform_action.setStatusTip("Add a new Moodle platform")
        add_platform_action.setToolTip("Add a new Moodle platform connection")
        add_platform_action.triggered.connect(self.on_add_platform_direct)
        toolbar.addAction(add_platform_action)

        # Platform manager action
        platform_manager_action = QAction("🏢 Platforms", self)
        platform_manager_action.setStatusTip("Manage Moodle platforms")
        platform_manager_action.setToolTip("Add, edit, and manage multiple Moodle platforms")
        platform_manager_action.triggered.connect(self.on_platform_manager)
        toolbar.addAction(platform_manager_action)

        # Platform switcher (combo box)
        self.platform_switcher = QComboBox()
        self.platform_switcher.setMinimumWidth(200)
        self.platform_switcher.setToolTip("Switch between Moodle platforms")
        self.platform_switcher.currentTextChanged.connect(self.on_platform_switch)
        toolbar.addWidget(self.platform_switcher)

        toolbar.addSeparator()

        # Browser section
        browser_action = QAction("🌐 Browser", self)
        browser_action.setStatusTip("Open Moodle in browser")
        browser_action.setToolTip("Open Moodle instance in web browser")
        browser_action.triggered.connect(self.on_open_browser)
        toolbar.addAction(browser_action)

        toolbar.addSeparator()

        # System section
        # System profile action
        self.system_profile_action = QAction("👤 Profile", self)
        self.system_profile_action.setStatusTip("View system user profile")
        self.system_profile_action.setToolTip("View and edit your system profile")
        self.system_profile_action.triggered.connect(self.on_system_profile)
        toolbar.addAction(self.system_profile_action)

        # System logout action
        self.system_logout_action = QAction("🚪 Logout", self)
        self.system_logout_action.setStatusTip("Logout from system")
        self.system_logout_action.setToolTip("Logout from system and exit")
        self.system_logout_action.triggered.connect(self.on_system_logout)
        toolbar.addAction(self.system_logout_action)

        toolbar.addSeparator()

        # Settings section
        settings_action = QAction("⚙️ Settings", self)
        settings_action.setStatusTip("Application settings")
        settings_action.setToolTip("Configure application settings")
        settings_action.triggered.connect(self.on_settings)
        toolbar.addAction(settings_action)

        # About action
        about_action = QAction("ℹ️ About", self)
        about_action.setStatusTip("About LMS Explorer")
        about_action.setToolTip("Show application information")
        about_action.triggered.connect(self.on_about)
        toolbar.addAction(about_action)

        # Exit action
        exit_action = QAction("❌ Exit", self)
        exit_action.setStatusTip("Exit application")
        exit_action.setToolTip("Close LMS Explorer")
        exit_action.triggered.connect(self.close)
        toolbar.addAction(exit_action)

    def apply_modern_style(self):
        """Apply modern styling to the application"""
        # Apply comprehensive modern stylesheet
        self.setStyleSheet(ModernStyles.get_main_window_style())
        
        # Set modern font
        ModernStyles.apply_modern_font(self, 'normal')

    def create_main_content_area(self, main_layout):
        """Create the main content area with enhanced layout"""
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_layout.addWidget(main_splitter)

        # Create left panel (tree view)
        left_panel = self.create_left_panel()

        # Create right panel (content area)
        right_panel = self.create_right_panel()

        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([500, 900])

    def create_left_panel(self):
        """Create the left panel with tree view and controls"""
        left_panel = QWidget()
        left_panel.setMinimumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # Filter section with modern styling
        filter_frame = QFrame()
        filter_frame.setStyleSheet(ModernStyles.get_frame_style())
        filter_layout = QVBoxLayout(filter_frame)

        # Filter input with enhanced styling
        filter_input_layout = QHBoxLayout()

        filter_label = QLabel("🔍 Filter:")
        filter_label.setStyleSheet(ModernStyles.get_label_style('subtitle'))

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search courses, categories, users...")
        self.filter_edit.setStyleSheet(ModernStyles.get_input_style())
        self.filter_edit.textChanged.connect(self.on_filter_changed)

        filter_input_layout.addWidget(filter_label)
        filter_input_layout.addWidget(self.filter_edit)

        # Quick filter buttons
        filter_buttons_layout = QHBoxLayout()

        courses_filter_btn = QPushButton("📚 Courses")
        courses_filter_btn.setStyleSheet(self.get_button_style('secondary'))
        courses_filter_btn.clicked.connect(lambda: self.quick_filter("course"))
        filter_buttons_layout.addWidget(courses_filter_btn)

        users_filter_btn = QPushButton("👥 Users")
        users_filter_btn.setStyleSheet(self.get_button_style('secondary'))
        users_filter_btn.clicked.connect(lambda: self.quick_filter("user"))
        filter_buttons_layout.addWidget(users_filter_btn)

        filter_layout.addLayout(filter_input_layout)
        filter_layout.addLayout(filter_buttons_layout)
        left_layout.addWidget(filter_frame)

        # Enhanced tree widget
        self.network_tree = NetworkTreeWidget()
        self.network_tree.setStyleSheet(ModernStyles.get_tree_style())
        
        # Connect network tree signals
        self.network_tree.item_selected.connect(self.on_tree_item_selected)
        self.network_tree.course_double_clicked.connect(self.on_course_double_clicked)
        
        left_layout.addWidget(self.network_tree)

        return left_panel

    def create_right_panel(self):
        """Create the right panel with content area"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # Create main content area with Moodle info page
        self.moodle_info_page = MoodleInfoPage()
        
        # Details browser for when connected to Moodle
        self.details_browser = QTextBrowser()
        self.details_browser.setReadOnly(True)
        
        # Stacked widget to switch between info page and details
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.moodle_info_page)
        self.content_stack.addWidget(self.details_browser)
        
        # Show info page by default
        self.content_stack.setCurrentWidget(self.moodle_info_page)
        
        # Add to right layout
        right_layout.addWidget(self.content_stack)

        # Content area header
        content_header = QFrame()
        content_header.setFrameStyle(QFrame.StyledPanel)
        content_header.setStyleSheet("QFrame { background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 5px; }")
        content_header_layout = QHBoxLayout(content_header)

        content_title = QLabel("📋 Content Area")
        content_title.setStyleSheet("color: #333; font-weight: bold; font-size: 12px;")

        content_header_layout.addWidget(content_title)
        content_header_layout.addStretch()
        right_layout.addWidget(content_header)

        # Enhanced content area
        self.content_area = QTreeWidget()
        self.content_area.setHeaderLabels(["Name", "Type", "Details"])
        self.content_area.setAlternatingRowColors(True)
        self.content_area.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QTreeWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        right_layout.addWidget(self.content_area)

        return right_panel

    def create_enhanced_status_bar(self):
        """Create enhanced status bar with connection info and progress"""
        self.status_bar = QStatusBar()

        self.statusBar().addPermanentWidget(QLabel(" | "))

        # Data count label
        self.data_label = QLabel("No data loaded")
        self.data_label.setStyleSheet("color: #666;")
        self.statusBar().addWidget(self.data_label)

        self.statusBar().addPermanentWidget(QLabel(" | "))

        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.statusBar().addPermanentWidget(self.progress_bar)

        self.setStatusBar(self.status_bar)

    def get_button_style(self, variant='primary'):
        """Get consistent button styling"""
        return ModernStyles.get_button_style(variant)

    def update_status_info(self):
        """Update status information periodically"""
        if self.lms_interface and self.lms_interface.is_connected():
            categories_count = len(self.lms_interface.get_categories())
            courses_count = len(self.lms_interface.get_courses())

            self.data_label.setText(f"Categories: {categories_count}, Courses: {courses_count}")
        else:
            self.data_label.setText("No data loaded")

    def quick_filter(self, filter_type):
        """Apply quick filter based on type"""
        if filter_type == "course":
            self.filter_edit.setText("course:")
        elif filter_type == "user":
            self.filter_edit.setText("user:")
        self.filter_edit.setFocus()

    def on_open_browser(self):
        """Handle browser action - open Moodle in web browser"""
        try:
            # Default Moodle URL
            moodle_url = "http://127.0.0.1/moodle/"

            # Try to get the configured URL from the LMS interface if connected
            if self.lms_interface and hasattr(self.lms_interface, 'get_host'):
                configured_host = self.lms_interface.get_host()
                if configured_host:
                    moodle_url = configured_host

            # Open URL in default web browser
            webbrowser.open(moodle_url)

            # Show status message
            self.statusBar().showMessage(f"Opening Moodle in browser: {moodle_url}", 3000)

        except Exception as e:
            QMessageBox.warning(self, "Browser Error",
                              f"Failed to open Moodle in browser: {str(e)}")
            self.statusBar().showMessage("Failed to open Moodle in browser", 3000)

    def on_export(self):
        """Handle export action"""
        if not self.lms_interface or not self.lms_interface.is_connected():
            QMessageBox.warning(self, "Not Connected", "Please connect to LMS first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "Excel files (*.xlsx);;CSV files (*.csv)"
        )

        if file_path:
            try:
                # Show progress
                self.show_progress(True, "Exporting data...")

                # Export data based on selected format
                if file_path.endswith('.xlsx'):
                    self.export_to_excel(file_path)
                elif file_path.endswith('.csv'):
                    self.export_to_csv(file_path)
                else:
                    # Default to CSV if no extension
                    self.export_to_csv(file_path)

                QMessageBox.information(self, "Export Complete", f"Data exported to {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
            finally:
                self.show_progress(False)

    def export_to_excel(self, file_path):
        """Export LMS data to Excel format"""
        try:
            import pandas as pd
            from datetime import datetime

            # Create data for export
            export_data = []

            # Export categories
            for category in self.lms_interface.get_categories():
                export_data.append({
                    'Type': 'Category',
                    'ID': category.get_id(),
                    'Name': category.get_name(),
                    'Courses Count': category.get_courses_count()
                })

                # Add courses in this category
                for course in category.get_courses():
                    export_data.append({
                        'Type': 'Course',
                        'ID': course.get_id(),
                        'Name': course.get_name(),
                        'Category': category.get_name(),
                        'Enrolled Users': len(course.get_enrolled_users()),
                        'User Groups': len(course.get_user_groups())
                    })

                    # Add enrolled users
                    for user in course.get_enrolled_users():
                        export_data.append({
                            'Type': 'User',
                            'ID': user.get_id(),
                            'Name': user.get_full_name(),
                            'Email': user.get_email(),
                            'Course': course.get_name(),
                            'Roles': ', '.join(user.get_roles())
                        })

            # Create DataFrame
            df = pd.DataFrame(export_data)

            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df['Export Date'] = timestamp

            # Export to Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='LMS Data', index=False)

                # Auto-adjust column widths
                worksheet = writer.sheets['LMS Data']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            print(f"Exported {len(export_data)} records to Excel: {file_path}")

        except ImportError:
            # Fallback to CSV if pandas not available
            self.export_to_csv(file_path.replace('.xlsx', '.csv'))
        except Exception as e:
            raise Exception(f"Excel export failed: {str(e)}")

    def export_to_csv(self, file_path):
        """Export LMS data to CSV format"""
        try:
            import csv
            from datetime import datetime

            # Create data for export
            export_data = []

            # Add header
            export_data.append(['Type', 'ID', 'Name', 'Additional Info', 'Export Date'])

            # Export categories
            for category in self.lms_interface.get_categories():
                export_data.append([
                    'Category',
                    str(category.get_id()),
                    category.get_name(),
                    f"Courses: {category.get_courses_count()}",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])

                # Add courses in this category
                for course in category.get_courses():
                    export_data.append([
                        'Course',
                        str(course.get_id()),
                        course.get_name(),
                        f"Category: {category.get_name()}",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ])

                    # Add enrolled users
                    for user in course.get_enrolled_users():
                        export_data.append([
                            'User',
                            str(user.get_id()),
                            user.get_full_name(),
                            f"Email: {user.get_email()}, Roles: {', '.join(user.get_roles())}",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ])

            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(export_data)

            print(f"Exported {len(export_data)-1} records to CSV: {file_path}")

        except Exception as e:
            raise Exception(f"CSV export failed: {str(e)}")

    def on_settings(self):
        """Handle settings action"""
        dialog = SettingsDialog(self)

        # Connect to settings changed signal to apply them immediately
        dialog.settings_changed.connect(self.apply_settings_from_dialog)

        dialog.exec_()

    def apply_settings_from_dialog(self, settings_dict):
        """Apply settings from the settings dialog"""
        # Apply theme settings
        theme = settings_dict.get('theme', 'system')
        self.apply_theme(theme)

        # Apply font settings
        font_family = settings_dict.get('font_family', 'Segoe UI')
        font_size = settings_dict.get('font_size', 9)
        self.apply_font_settings(font_family, font_size)

        # Apply tree view settings
        show_icons = settings_dict.get('show_icons', True)
        alternate_colors = settings_dict.get('alternate_colors', True)
        self.apply_tree_view_settings(show_icons, alternate_colors)

        # Apply window settings
        default_width = settings_dict.get('default_width', 1400)
        default_height = settings_dict.get('default_height', 900)
        self.resize(default_width, default_height)

        # Show confirmation
        self.statusBar().showMessage("Settings applied successfully", 3000)

    def apply_theme(self, theme):
        """Apply theme settings"""
        palette = QPalette()

        if theme == "dark":
            # Dark theme colors
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
            palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        else:
            # Light theme (default)
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, QColor(33, 33, 33))
            palette.setColor(QPalette.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ToolTipText, QColor(33, 33, 33))
            palette.setColor(QPalette.Text, QColor(33, 33, 33))
            palette.setColor(QPalette.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ButtonText, QColor(33, 33, 33))
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

        self.setPalette(palette)

    def apply_font_settings(self, font_family, font_size):
        """Apply font settings"""
        font = QFont(font_family, font_size)
        self.setFont(font)

        # Update all child widgets
        for widget in self.findChildren(QWidget):
            widget.setFont(font)

    def apply_tree_view_settings(self, show_icons, alternate_colors):
        """Apply tree view settings"""
        # Update the network tree styling based on settings
        if show_icons:
            # Icons are already enabled in the tree widget
            # The tree widget uses icons by default
            pass
        else:
            # Hide icons - we can modify the icon display in the tree widget
            # This would require modifying the NetworkTreeWidget to support icon visibility
            pass

        # Update alternating colors
        self.network_tree.setAlternatingRowColors(alternate_colors)

    def show_progress(self, visible, message="Processing..."):
        """Show or hide progress bar"""
        if self.progress_bar:
            self.progress_bar.setVisible(visible)
            if visible:
                self.progress_bar.setRange(0, 0)  # Indeterminate progress
                self.statusBar().showMessage(message)
            else:
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)

    def create_menu_bar(self):
        """Create the menu bar"""
        # For minimal UI, we're not creating any menus
        # All functionality is accessible through the toolbar
        pass
        
    def load_config(self):
        """Load configuration from config file"""
        config_path = os.path.join(os.path.dirname(sys.executable), 'config.ini')
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
            
        if os.path.exists(config_path):
            self.config_manager.load_config(config_path)
            self.statusBar().showMessage(f"Configuration loaded from {config_path}")
        else:
            self.statusBar().showMessage("No configuration file found")
            
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
        
    def on_tree_item_selected(self, item_data):
        """Handle tree item selection"""
        if hasattr(item_data, 'course_content'):
            # It's a course, load its content
            self.load_course_content(item_data)
        elif hasattr(item_data, 'full_name'):
            # It's a user, show user info
            self.show_user_info(item_data)
            
    def on_course_double_clicked(self, course):
        """Handle course double-click - load course content"""
        self.load_course_content(course)
        
    def load_course_content(self, course):
        """Load and display course content in the content area"""
        if not course:
            return
            
        try:
            # Clear current content
            self.content_area.clear()
            
            # Set content area header
            self.content_area.setHeaderLabels(["Section", "Module", "Content", "File"])
            
            # Load course content
            course_content = course.get_course_content()
            
            if not course_content:
                # Try to load content from LMS
                course.get_course_content_from_lms()
                course_content = course.get_course_content()
            
            if course_content:
                for section in course_content:
                    section_item = QTreeWidgetItem(self.content_area)
                    section_item.setText(0, section.name or f"Section {section.id}")
                    section_item.setText(1, "")
                    section_item.setText(2, "")
                    section_item.setText(3, "")
                    
                    # Add modules to section
                    for module in section.modules:
                        module_item = QTreeWidgetItem(section_item)
                        module_item.setText(0, "")
                        module_item.setText(1, module.name or f"Module {module.id}")
                        module_item.setText(2, module.mod_type or "unknown")
                        module_item.setText(3, "")
                        
                        # Add contents to module
                        for content in module.contents:
                            content_item = QTreeWidgetItem(module_item)
                            content_item.setText(0, "")
                            content_item.setText(1, "")
                            content_item.setText(2, content.file_name or "File")
                            content_item.setText(3, content.file_type or "unknown")
                            
                    # Expand section
                    section_item.setExpanded(True)
                    
                # Auto-resize columns
                self.content_area.header().resizeSections(QHeaderView.ResizeToContents)
                
                # Update status bar
                self.statusBar().showMessage(f"Loaded content for course: {course.name}")
            else:
                # No content available
                no_content_item = QTreeWidgetItem(self.content_area)
                no_content_item.setText(0, "No course content available")
                no_content_item.setText(1, "")
                no_content_item.setText(2, "")
                no_content_item.setText(3, "")
                
                self.statusBar().showMessage(f"No content available for course: {course.name}")
                
        except Exception as e:
            # Show error in content area
            error_item = QTreeWidgetItem(self.content_area)
            error_item.setText(0, f"Error loading course content: {str(e)}")
            error_item.setText(1, "")
            error_item.setText(2, "")
            error_item.setText(3, "")
            
            self.statusBar().showMessage(f"Error loading course content: {str(e)}")
            
    def show_user_info(self, user):
        """Show user information in the content area"""
        if not user:
            return
            
        try:
            # Clear current content
            self.content_area.clear()
            
            # Set content area header for user info
            self.content_area.setHeaderLabels(["Property", "Value"])
            
            # Add user information
            user_info = [
                ("Name", user.get_full_name()),
                ("Username", getattr(user, 'username', '')),
                ("Email", user.get_email()),
                ("ID", str(user.get_id())),
                ("First Name", user.get_first_name()),
                ("Last Name", getattr(user, 'last_name', '')),
            ]
            
            for property_name, value in user_info:
                if value:  # Only show non-empty values
                    item = QTreeWidgetItem(self.content_area)
                    item.setText(0, property_name)
                    item.setText(1, str(value))
                    
            # Auto-resize columns
            self.content_area.header().resizeSections(QHeaderView.ResizeToContents)
            
            # Update status bar
            self.statusBar().showMessage(f"Showing user info for: {user.get_full_name()}")
            
        except Exception as e:
            # Show error
            error_item = QTreeWidgetItem(self.content_area)
            error_item.setText(0, "Error loading user info")
            error_item.setText(1, str(e))
            
            self.statusBar().showMessage(f"Error loading user info: {str(e)}")
        
    def on_login_successful(self, connection_details):
        """Handle successful login"""
        try:
            # Extract connection details
            host = connection_details['host']
            username = connection_details['username']
            service = connection_details['service']
            remember_me = connection_details['remember_me']
            site_info = connection_details['site_info']
            
            # Set LMS details
            self.lms_interface.set_host(host)
            self.lms_interface.set_name("Moodle")
            
            # Connect to LMS (use password from connection details)
            self.statusBar().showMessage("Connecting to LMS...")
            
            password = connection_details.get('password', '')
            
            if self.lms_interface.connect(username, password, service):
                self.statusBar().showMessage("Connected to LMS")
                
                # Create user session
                current_user = self.lms_interface.get_user()
                if current_user:
                    session_success = self.session_manager.login(
                        user=current_user,
                        lms=self.lms_interface,
                        host=host,
                        password=password,
                        service=service,
                        remember_me=remember_me
                    )
                    if session_success:
                        self.profile_action.setEnabled(True)
                        self.statusBar().showMessage(f"Connected as {current_user.get_full_name()}")
                
                # Update the network tree with loaded data
                self.network_tree.set_lms(self.lms_interface)
                
                # Save server configuration to database
                server_id = self.database_manager.save_moodle_server(
                    name="Moodle",
                    host=host,
                    port=80,  # Default Moodle port
                    service_name=service,
                    description=f"Moodle instance at {host}"
                )

                if server_id > 0:
                    # Save credentials if remember me is checked
                    if remember_me:
                        self.database_manager.save_credentials(
                            server_id=server_id,
                            server_type='moodle',
                            username=username,
                            password=password,  # Password is stored encrypted in database
                            is_remembered=remember_me
                        )

                    # Log successful connection
                    self.database_manager.log_connection(
                        server_id=server_id,
                        server_type='moodle',
                        success=True,
                        response_time_ms=0,  # Could be enhanced to measure actual time
                        user_agent="MoodleManager/1.0"
                    )

                # Save configuration
                self.config_manager.add_config(
                    name="Moodle",
                    url=host,
                    username=username,
                    password="",  # Don't store password in config anymore
                    service=service,
                    remember_me=remember_me
                )
                self.config_manager.save_config()
                
                print(f"Successfully connected and loaded {len(self.lms_interface.get_categories())} categories and {len(self.lms_interface.get_courses())} courses")
            else:
                self.statusBar().showMessage("Connection failed")
                print("Failed to connect to LMS")
                
        except Exception as e:
            self.statusBar().showMessage(f"Login processing error: {e}")
            print(f"Error processing login: {e}")
    
    def on_login_failed(self, error_message):
        """Handle login failure"""
        self.statusBar().showMessage("Login failed")
        print(f"Login failed: {error_message}")
    
    def on_credentials_stored(self, success):
        """Handle credential storage result"""
        if success:
            self.statusBar().showMessage("Credentials stored securely")
        else:
            self.statusBar().showMessage("Warning: Failed to store credentials")
            
    def on_about(self):
        """Handle about action"""
        dialog = AboutDialog(self)
        dialog.exec_()
        
    def on_refresh(self):
        """Handle refresh action"""
        if self.lms_interface and self.lms_interface.is_connected():
            self.statusBar().showMessage("Refreshing data from LMS...")
            # Refresh the network tree
            self.network_tree.refresh_data()
            self.statusBar().showMessage("Data refreshed successfully")
        else:
            self.statusBar().showMessage("Not connected to LMS")
            QMessageBox.warning(self, "Not Connected", "Please connect to LMS first.")
    
    def on_moodle_login_successful(self, connection_details):
        """Handle successful Moodle login"""
        try:
            host = connection_details.get('host')
            username = connection_details.get('username')
            password = connection_details.get('password')
            service = connection_details.get('service', 'moodle_mobile_app')
            remember_me = connection_details.get('remember_me', False)

            # Connect to LMS
            if self.lms_interface.connect(username, password, service):
                self.statusBar().showMessage("Connected to LMS")
                
                # Create user session
                current_user = self.lms_interface.get_user()
                if current_user:
                    session_success = self.session_manager.login(
                        user=current_user,
                        lms=self.lms_interface,
                        host=host,
                        password=password,
                        service=service,
                        remember_me=remember_me
                    )
                    if session_success:
                        self.statusBar().showMessage(f"Connected as {current_user.get_full_name()}")
                
                # Switch to details view and load Moodle data
                self.content_stack.setCurrentWidget(self.details_browser)
                self.details_browser.setHtml(f"<h2>Connected to Moodle</h2><p>Successfully connected to {host}</p>")
                
                # Save server configuration
                self.save_server_config(host, username, service, remember_me)
                
                logger.info(f"Successfully connected to LMS: {host}")
            else:
                QMessageBox.warning(self, "Connection Failed", 
                                  "Failed to connect to the LMS. Please check your credentials.")
                
        except Exception as e:
            logger.error(f"Error in Moodle login success handler: {e}")
            QMessageBox.critical(self, "Login Error", 
                               f"An error occurred during login: {str(e)}")

    def on_moodle_login_failed(self, error_message):
        """Handle Moodle login failure"""
        QMessageBox.warning(self, "Login Failed", f"Login failed: {error_message}")

    def on_system_profile(self):
        """Handle system profile action"""
        if not self.system_user:
            QMessageBox.warning(self, "No System User", "No system user session found.")
            return
            
        # Show system profile dialog
        profile_dialog = SystemProfileDialog(self.system_user, self)
        profile_dialog.profile_updated.connect(self.on_system_profile_updated)
        profile_dialog.password_changed.connect(self.on_system_password_changed)
        profile_dialog.exec_()
        
    def on_system_profile_updated(self, updated_data):
        """Handle system profile update"""
        try:
            # Update local system user data
            self.system_user.update(updated_data)
            
            # Update window title if name changed
            username = self.system_user.get('username', 'Unknown')
            self.setWindowTitle(f"LMS Explorer - {username}")
            
            # Update status bar
            full_name = self.system_user.get('full_name', username)
            self.statusBar().showMessage(f"Logged in as: {full_name}")
            
            self.statusBar().showMessage("System profile updated successfully")
        except Exception as e:
            logger.error(f"Error handling system profile update: {e}")
            self.statusBar().showMessage("System profile update completed")
        
    def on_system_password_changed(self):
        """Handle system password change"""
        QMessageBox.information(self, "Password Changed", 
                              "Your system password has been changed successfully.")
        
    def on_system_logout(self):
        """Handle system logout"""
        reply = QMessageBox.question(self, "Confirm System Logout", 
                                   "Are you sure you want to logout from the system?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Destroy system session
            if self.system_session_token:
                self.system_user_manager.destroy_session(self.system_session_token)
            
            # Logout from Moodle if connected
            if self.session_manager.is_logged_in():
                self.session_manager.logout()
            
            # Close application
            self.close()
    
    def setup_platform_ui(self):
        """Setup platform-related UI components"""
        self.update_platform_switcher()
    
    def update_platform_switcher(self):
        """Update the platform switcher combo box"""
        self.platform_switcher.clear()
        self.platform_switcher.addItem("Select Platform...", None)
        
        platforms = self.multi_platform_manager.get_active_platforms()
        for platform in platforms:
            status_icon = "🟢" if platform.status.value == "connected" else "🔴"
            display_text = f"{status_icon} {platform.name}"
            self.platform_switcher.addItem(display_text, platform.id)
        
        # Set current platform if any
        active_platform = self.multi_platform_manager.get_active_platform()
        if active_platform:
            for i in range(1, self.platform_switcher.count()):
                if self.platform_switcher.itemData(i) == active_platform.id:
                    self.platform_switcher.setCurrentIndex(i)
                    break
    
    def on_platform_manager(self):
        """Handle platform manager action"""
        dialog = PlatformManagerDialog(parent=self)
        dialog.platform_selected.connect(self.on_platform_selected)
        if dialog.exec_() == QDialog.Accepted:
            self.update_platform_switcher()
    
    def on_add_platform_direct(self):
        """Handle direct add platform action"""
        from ui.dialogs.platform_manager_dialog import PlatformEditDialog
        dialog = PlatformEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            platform = dialog.get_platform()
            self.multi_platform_manager.add_platform(platform)
            self.update_platform_switcher()
            self.statusBar().showMessage(f"Added platform: {platform.name}")
            
    def on_platform_selected(self, platform_id: str):
        """Handle platform selection from manager"""
        self.multi_platform_manager.set_active_platform(platform_id)
        self.update_platform_switcher()
        
        platform = self.multi_platform_manager.get_platform(platform_id)
        if platform:
            self.statusBar().showMessage(f"Switched to platform: {platform.name}")
            # Update window title
            username = self.system_user.get('username', 'Unknown') if self.system_user else 'Unknown'
            self.setWindowTitle(f"LMS Explorer - {username} - {platform.name}")
    
    def on_platform_switch(self, platform_name: str):
        """Handle platform switch from combo box"""
        platform_id = self.platform_switcher.currentData()
        if platform_id and platform_id != self.multi_platform_manager.active_platform_id:
            self.multi_platform_manager.set_active_platform(platform_id)
            
            platform = self.multi_platform_manager.get_platform(platform_id)
            if platform:
                self.statusBar().showMessage(f"Switched to platform: {platform.name}")
                # Update window title
                username = self.system_user.get('username', 'Unknown') if self.system_user else 'Unknown'
                self.setWindowTitle(f"LMS Explorer - {username} - {platform.name}")
                
                # Load platform-specific data
                self.load_platform_data(platform)
    
    def load_platform_data(self, platform):
        """Load data for the selected platform"""
        try:
            # Update status to show we're loading
            self.statusBar().showMessage(f"Loading data from {platform.name}...")
            
            # Configure LMS interface with platform details
            self.lms_interface.set_host(platform.url)
            self.lms_interface.set_name(platform.name)
            
            # Attempt to connect using platform credentials
            # Note: In a real scenario, we would use the stored token or credentials
            # For now, we'll try to connect if we have credentials
            connected = False
            if platform.credentials.token:
                # If we have a token, we might need a method to connect with token
                # For now, assuming connect() handles it or we simulate it
                connected = True # Placeholder for token connection
            elif platform.credentials.username and platform.credentials.password:
                connected = self.lms_interface.connect(
                    platform.credentials.username, 
                    platform.credentials.password
                )
            
            if connected or platform.status.value == "connected":
                # Update the network tree with loaded data
                self.network_tree.set_lms(self.lms_interface)
                self.statusBar().showMessage(f"Connected to {platform.name}")
            else:
                self.statusBar().showMessage(f"Platform {platform.name} is not connected. Please connect first.")
                # Clear tree or show disconnected state
                self.network_tree.clear()
                
        except Exception as e:
            logger.error(f"Error loading data from {platform.name}: {str(e)}")
            self.statusBar().showMessage(f"Error loading data: {str(e)}")
            
            # Add some sample categories
            self.network_tree.add_child(categories_item, "Sample Category 1")
            self.network_tree.add_child(categories_item, "Sample Category 2")
            
            # Add some sample courses
            self.network_tree.add_child(courses_item, "Sample Course 1")
            self.network_tree.add_child(courses_item, "Sample Course 2")
            
            # Add some sample users
            self.network_tree.add_child(users_item, "Students")
            self.network_tree.add_child(users_item, "Teachers")
        
    def get_current_platform(self):
        """Get the currently active platform"""
        return self.multi_platform_manager.get_active_platform()
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save configuration if needed
        event.accept()
