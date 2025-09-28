"""
Main Window for LMS Explorer
Enhanced UI with modern styling and improved functionality
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QMenuBar, QMenu, QAction, QStatusBar, QSplitter,
                             QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
                             QMessageBox, QFileDialog, QProgressBar, QLabel,
                             QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPalette

from data_models import LMS
from config_manager import ConfigManager, LMSConfig
from tree_views.network_tree import NetworkTreeWidget
from dialogs.about_dialog import AboutDialog
from dialogs.lms_dialog import LMSDialog
from dialogs.settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.lms_interface = LMS()
        self.config_manager = ConfigManager()
        
        self.init_ui()
        self.load_config()
        
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

        # Connection section
        connect_action = QAction("🔗 Connect", self)
        connect_action.setStatusTip("Connect to LMS")
        connect_action.setToolTip("Connect to Learning Management System")
        connect_action.triggered.connect(self.on_connect)
        toolbar.addAction(connect_action)

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
        # Set modern color palette
        palette = QPalette()

        # Modern dark theme colors
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

        # Set modern font
        font = QFont("Segoe UI", 9)
        self.setFont(font)

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
        filter_frame.setFrameStyle(QFrame.StyledPanel)
        filter_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #ddd; border-radius: 5px; }")
        filter_layout = QVBoxLayout(filter_frame)

        # Filter input with enhanced styling
        filter_input_layout = QHBoxLayout()

        filter_label = QLabel("🔍 Filter:")
        filter_label.setStyleSheet("color: #333; font-weight: bold;")

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search courses, categories, users...")
        self.filter_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        self.filter_edit.textChanged.connect(self.on_filter_changed)

        filter_input_layout.addWidget(filter_label)
        filter_input_layout.addWidget(self.filter_edit)

        # Quick filter buttons
        filter_buttons_layout = QHBoxLayout()

        courses_filter_btn = QPushButton("📚 Courses")
        courses_filter_btn.setStyleSheet(self.get_button_style())
        courses_filter_btn.clicked.connect(lambda: self.quick_filter("course"))
        filter_buttons_layout.addWidget(courses_filter_btn)

        users_filter_btn = QPushButton("👥 Users")
        users_filter_btn.setStyleSheet(self.get_button_style())
        users_filter_btn.clicked.connect(lambda: self.quick_filter("user"))
        filter_buttons_layout.addWidget(users_filter_btn)

        filter_layout.addLayout(filter_input_layout)
        filter_layout.addLayout(filter_buttons_layout)
        left_layout.addWidget(filter_frame)

        # Enhanced tree widget
        self.network_tree = NetworkTreeWidget()
        self.network_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        left_layout.addWidget(self.network_tree)

        return left_panel

    def create_right_panel(self):
        """Create the right panel with content area"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(5, 5, 5, 5)

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

        # Connection status label
        self.connection_label = QLabel("🔴 Disconnected")
        self.connection_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        self.statusBar().addWidget(self.connection_label)

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

    def get_button_style(self):
        """Get consistent button styling"""
        return """
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 12px;
                background-color: #f8f9fa;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #0078d4;
            }
            QPushButton:pressed {
                background-color: #0078d4;
                color: white;
            }
        """

    def update_status_info(self):
        """Update status information periodically"""
        if self.lms_interface and self.lms_interface.is_connected():
            categories_count = len(self.lms_interface.get_categories())
            courses_count = len(self.lms_interface.get_courses())

            self.connection_label.setText("🟢 Connected")
            self.connection_label.setStyleSheet("color: #2e7d32; font-weight: bold;")

            self.data_label.setText(f"Categories: {categories_count}, Courses: {courses_count}")
        else:
            self.connection_label.setText("🔴 Disconnected")
            self.connection_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
            self.data_label.setText("No data loaded")

    def quick_filter(self, filter_type):
        """Apply quick filter based on type"""
        if filter_type == "course":
            self.filter_edit.setText("course:")
        elif filter_type == "user":
            self.filter_edit.setText("user:")
        self.filter_edit.setFocus()

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
            
            # Check for auto-connect configuration
            autoconnect_config = self.config_manager.get_autoconnect_config()
            if autoconnect_config:
                # Auto-connect to the configured LMS
                self.auto_connect_to_lms(autoconnect_config)
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
            self.statusBar().showMessage("Connecting to LMS...")
            
            if self.lms_interface.connect(username, password, service):
                self.statusBar().showMessage("Connected to LMS")
                
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
                self.statusBar().showMessage("Connection failed")
                print("Failed to connect to LMS")
            
    def auto_connect_to_lms(self, config):
        """Auto-connect to LMS using the provided configuration"""
        self.statusBar().showMessage(f"Auto-connecting to {config.name}...")
        
        # Set LMS details
        self.lms_interface.set_host(config.url)
        self.lms_interface.set_name(config.name)
        
        # Connect to LMS
        if self.lms_interface.connect(config.username, config.password, config.service):
            self.statusBar().showMessage(f"Auto-connected to {config.name}")
            
            # Update the network tree with loaded data
            self.network_tree.set_lms(self.lms_interface)
            
            print(f"Auto-connected successfully and loaded {len(self.lms_interface.get_categories())} categories and {len(self.lms_interface.get_courses())} courses")
        else:
            self.statusBar().showMessage(f"Auto-connect failed for {config.name}")
            print(f"Failed to auto-connect to {config.name}")
    
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
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save configuration if needed
        event.accept()
