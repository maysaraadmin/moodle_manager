"""
Section Form
Form for displaying section information and details
"""

from typing import Optional
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QGroupBox,
                             QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import ISection, ICourse, IModule


class SectionForm(QDialog):
    """Form for displaying section information and details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.section: Optional[ISection] = None
        self.course: Optional[ICourse] = None
        
        self.setup_ui()
        self.setup_actions()
        
    def setup_ui(self):
        """Setup the form UI"""
        self.setWindowTitle("Section Information")
        self.resize(600, 500)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create info tab
        self.create_info_tab()
        
        # Create modules tab
        self.create_modules_tab()
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Add buttons
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
        
    def create_info_tab(self):
        """Create the section information tab"""
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
        
        self.section_number_edit = QLineEdit()
        self.section_number_edit.setReadOnly(True)
        basic_layout.addRow("Section Number:", self.section_number_edit)
        
        self.visible_edit = QLineEdit()
        self.visible_edit.setReadOnly(True)
        basic_layout.addRow("Visible:", self.visible_edit)
        
        self.highlight_edit = QLineEdit()
        self.highlight_edit.setReadOnly(True)
        basic_layout.addRow("Highlight:", self.highlight_edit)
        
        info_layout.addWidget(basic_group)
        
        # Additional information group
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout(additional_group)
        
        self.summary_edit = QLineEdit()
        self.summary_edit.setReadOnly(True)
        additional_layout.addRow("Summary:", self.summary_edit)
        
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
        
    def create_modules_tab(self):
        """Create the section modules tab"""
        modules_widget = QWidget()
        modules_layout = QVBoxLayout(modules_widget)
        
        # Modules table
        self.modules_table = QTableWidget()
        self.modules_table.setColumnCount(5)
        self.modules_table.setHorizontalHeaderLabels(["Name", "Type", "Visible", "Highlight", "Position"])
        
        # Set table properties
        header = self.modules_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.modules_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.modules_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.modules_table.setAlternatingRowColors(True)
        
        modules_layout.addWidget(self.modules_table)
        
        self.tab_widget.addTab(modules_widget, "Modules")
        
    def setup_actions(self):
        """Setup actions and signals"""
        # Connect table double click
        self.modules_table.doubleClicked.connect(self.on_module_double_clicked)
        
    def set_section(self, section: ISection, course: Optional[ICourse] = None):
        """Set the section and update the form"""
        self.section = section
        self.course = course
        
        if section:
            self.setWindowTitle(f"Section: {section.name}")
            self.update_section_info()
            self.update_modules_table()
            self.update_button_states()
        else:
            self.setWindowTitle("Section Information")
            self.clear_form()
            
    def update_section_info(self):
        """Update section information fields"""
        if not self.section:
            return
            
        self.id_label.setText(str(self.section.id))
        self.name_edit.setText(self.section.name or "")
        self.section_number_edit.setText(str(self.section.section_number) if self.section.section_number is not None else "")
        self.visible_edit.setText(str(self.section.visible) if self.section.visible is not None else "")
        self.highlight_edit.setText(str(self.section.highlight) if self.section.highlight is not None else "")
        self.summary_edit.setText(self.section.summary or "")
        self.time_created_edit.setText(self.section.time_created or "")
        self.time_modified_edit.setText(self.section.time_modified or "")
        self.description_edit.setText(self.section.description or "")
        self.notes_edit.setText(self.section.notes or "")
        
    def update_modules_table(self):
        """Update the modules table"""
        self.modules_table.setRowCount(0)
        
        if not self.section:
            return
            
        # This would typically load section modules from the LMS
        # For now, we'll show a placeholder
        # In a real implementation, you would get the section's modules
        pass
        
    def update_button_states(self):
        """Update button enabled states"""
        enabled = self.section is not None
        self.refresh_button.setEnabled(enabled)
        
    def refresh_data(self):
        """Refresh section data"""
        if self.section:
            self.update_section_info()
            self.update_modules_table()
            
    def on_module_double_clicked(self, index):
        """Handle module double click"""
        # This would typically open a module form
        pass
        
    def clear_form(self):
        """Clear all form fields"""
        self.id_label.setText("")
        self.name_edit.setText("")
        self.section_number_edit.setText("")
        self.visible_edit.setText("")
        self.highlight_edit.setText("")
        self.summary_edit.setText("")
        self.time_created_edit.setText("")
        self.time_modified_edit.setText("")
        self.description_edit.setText("")
        self.notes_edit.setText("")
        self.modules_table.setRowCount(0)
        
    def closeEvent(self, event):
        """Handle form close event"""
        # Clean up resources
        self.clear_form()
        super().closeEvent(event)
