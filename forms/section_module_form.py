"""
Section Module Form
Form for displaying section module information and details
"""

from typing import Optional
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QGroupBox,
                             QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import IModule, ICourse, ISection, IContent


class SectionModuleForm(QDialog):
    """Form for displaying section module information and details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.module: Optional[IModule] = None
        self.course: Optional[ICourse] = None
        self.section: Optional[ISection] = None
        
        self.setup_ui()
        self.setup_actions()
        
    def setup_ui(self):
        """Setup the form UI"""
        self.setWindowTitle("Section Module Information")
        self.resize(600, 500)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create info tab
        self.create_info_tab()
        
        # Create contents tab
        self.create_contents_tab()
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Add buttons
        self.open_in_browser_button = QPushButton("Open in Browser")
        self.open_in_browser_button.clicked.connect(self.open_in_browser)
        button_layout.addWidget(self.open_in_browser_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
        
    def create_info_tab(self):
        """Create the module information tab"""
        info_widget = QWidget()
        info_layout = QFormLayout(info_widget)
        
        # Basic information group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.id_label = QLabel()
        basic_layout.addRow("ID:", self.id_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        basic_layout.addRow("Name:", self.name_edit)
        
        self.instance_edit = QLineEdit()
        self.instance_edit.setReadOnly(True)
        basic_layout.addRow("Instance:", self.instance_edit)
        
        self.modname_edit = QLineEdit()
        self.modname_edit.setReadOnly(True)
        basic_layout.addRow("Module Name:", self.modname_edit)
        
        self.modplural_edit = QLineEdit()
        self.modplural_edit.setReadOnly(True)
        basic_layout.addRow("Module Plural:", self.modplural_edit)
        
        info_layout.addWidget(basic_group)
        
        # Position and visibility group
        position_group = QGroupBox("Position and Visibility")
        position_layout = QFormLayout(position_group)
        
        self.position_edit = QLineEdit()
        self.position_edit.setReadOnly(True)
        position_layout.addRow("Position:", self.position_edit)
        
        self.visible_edit = QLineEdit()
        self.visible_edit.setReadOnly(True)
        position_layout.addRow("Visible:", self.visible_edit)
        
        self.highlight_edit = QLineEdit()
        self.highlight_edit.setReadOnly(True)
        position_layout.addRow("Highlight:", self.highlight_edit)
        
        self.uservisible_edit = QLineEdit()
        self.uservisible_edit.setReadOnly(True)
        position_layout.addRow("User Visible:", self.uservisible_edit)
        
        info_layout.addWidget(position_group)
        
        # Additional information group
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout(additional_group)
        
        self.indent_edit = QLineEdit()
        self.indent_edit.setReadOnly(True)
        additional_layout.addRow("Indent:", self.indent_edit)
        
        self.time_created_edit = QLineEdit()
        self.time_created_edit.setReadOnly(True)
        additional_layout.addRow("Time Created:", self.time_created_edit)
        
        self.time_modified_edit = QLineEdit()
        self.time_modified_edit.setReadOnly(True)
        additional_layout.addRow("Time Modified:", self.time_modified_edit)
        
        info_layout.addWidget(additional_group)
        
        # Description group
        description_group = QGroupBox("Description")
        description_layout = QVBoxLayout(description_group)
        
        self.description_edit = QTextEdit()
        self.description_edit.setReadOnly(True)
        description_layout.addWidget(self.description_edit)
        
        info_layout.addWidget(description_group)
        
        # Notes group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setReadOnly(True)
        notes_layout.addWidget(self.notes_edit)
        
        info_layout.addWidget(notes_group)
        
        self.tab_widget.addTab(info_widget, "Information")
        
    def create_contents_tab(self):
        """Create the module contents tab"""
        contents_widget = QWidget()
        contents_layout = QVBoxLayout(contents_widget)
        
        # Contents table
        self.contents_table = QTableWidget()
        self.contents_table.setColumnCount(6)
        self.contents_table.setHorizontalHeaderLabels(["Name", "Type", "MIME Type", "Size", "Time Modified", "Visible"])
        
        # Set table properties
        header = self.contents_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.contents_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.contents_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.contents_table.setAlternatingRowColors(True)
        
        contents_layout.addWidget(self.contents_table)
        
        self.tab_widget.addTab(contents_widget, "Contents")
        
    def setup_actions(self):
        """Setup actions and signals"""
        # Connect table double click
        self.contents_table.doubleClicked.connect(self.on_content_double_clicked)
        
    def set_module(self, module: IModule, course: Optional[ICourse] = None, section: Optional[ISection] = None):
        """Set the module and update the form"""
        self.module = module
        self.course = course
        self.section = section
        
        if module:
            self.setWindowTitle(f"Section Module: {module.name}")
            self.update_module_info()
            self.update_contents_table()
            self.update_button_states()
        else:
            self.setWindowTitle("Section Module Information")
            self.clear_form()
            
    def update_module_info(self):
        """Update module information fields"""
        if not self.module:
            return
            
        self.id_label.setText(str(self.module.id))
        self.name_edit.setText(self.module.name or "")
        self.instance_edit.setText(str(self.module.instance) if self.module.instance is not None else "")
        self.modname_edit.setText(self.module.modname or "")
        self.modplural_edit.setText(self.module.modplural or "")
        self.position_edit.setText(str(self.module.position) if self.module.position is not None else "")
        self.visible_edit.setText(str(self.module.visible) if self.module.visible is not None else "")
        self.highlight_edit.setText(str(self.module.highlight) if self.module.highlight is not None else "")
        self.uservisible_edit.setText(str(self.module.uservisible) if self.module.uservisible is not None else "")
        self.indent_edit.setText(str(self.module.indent) if self.module.indent is not None else "")
        self.time_created_edit.setText(self.module.time_created or "")
        self.time_modified_edit.setText(self.module.time_modified or "")
        self.description_edit.setText(self.module.description or "")
        self.notes_edit.setText(self.module.notes or "")
        
    def update_contents_table(self):
        """Update the contents table"""
        self.contents_table.setRowCount(0)
        
        if not self.module:
            return
            
        # This would typically load module contents from the LMS
        # For now, we'll show a placeholder
        # In a real implementation, you would get the module's contents
        pass
        
    def update_button_states(self):
        """Update button enabled states"""
        enabled = self.module is not None
        self.open_in_browser_button.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)
        
    def open_in_browser(self):
        """Open module in browser"""
        if self.module and self.course:
            # This would typically open the module in a browser
            pass
            
    def refresh_data(self):
        """Refresh module data"""
        if self.module:
            self.update_module_info()
            self.update_contents_table()
            
    def on_content_double_clicked(self, index):
        """Handle content double click"""
        # This would typically open a content form
        pass
        
    def clear_form(self):
        """Clear all form fields"""
        self.id_label.setText("")
        self.name_edit.setText("")
        self.instance_edit.setText("")
        self.modname_edit.setText("")
        self.modplural_edit.setText("")
        self.position_edit.setText("")
        self.visible_edit.setText("")
        self.highlight_edit.setText("")
        self.uservisible_edit.setText("")
        self.indent_edit.setText("")
        self.time_created_edit.setText("")
        self.time_modified_edit.setText("")
        self.description_edit.setText("")
        self.notes_edit.setText("")
        self.contents_table.setRowCount(0)
        
    def closeEvent(self, event):
        """Handle form close event"""
        # Clean up resources
        self.clear_form()
        super().closeEvent(event)
