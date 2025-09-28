"""
Users Group Form
Form for displaying users group information and details
"""

from typing import Optional
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QGroupBox,
                             QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import IUsersGroup, ICourse, IUser


class UsersGroupForm(QDialog):
    """Form for displaying users group information and details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.group: Optional[IUsersGroup] = None
        self.course: Optional[ICourse] = None
        
        self.setup_ui()
        self.setup_actions()
        
    def setup_ui(self):
        """Setup the form UI"""
        self.setWindowTitle("Users Group Information")
        self.resize(600, 500)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create info tab
        self.create_info_tab()
        
        # Create members tab
        self.create_members_tab()
        
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
        """Create the group information tab"""
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
        
        self.description_edit = QLineEdit()
        self.description_edit.setReadOnly(True)
        basic_layout.addRow("Description:", self.description_edit)
        
        self.id_number_edit = QLineEdit()
        self.id_number_edit.setReadOnly(True)
        basic_layout.addRow("ID Number:", self.id_number_edit)
        
        info_layout.addWidget(basic_group)
        
        # Additional information group
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout(additional_group)
        
        self.enrolment_key_edit = QLineEdit()
        self.enrolment_key_edit.setReadOnly(True)
        additional_layout.addRow("Enrolment Key:", self.enrolment_key_edit)
        
        self.picture_edit = QLineEdit()
        self.picture_edit.setReadOnly(True)
        additional_layout.addRow("Picture:", self.picture_edit)
        
        self.time_created_edit = QLineEdit()
        self.time_created_edit.setReadOnly(True)
        additional_layout.addRow("Time Created:", self.time_created_edit)
        
        self.time_modified_edit = QLineEdit()
        self.time_modified_edit.setReadOnly(True)
        additional_layout.addRow("Time Modified:", self.time_modified_edit)
        
        info_layout.addWidget(additional_group)
        
        # Notes group
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setReadOnly(True)
        notes_layout.addWidget(self.notes_edit)
        
        info_layout.addWidget(notes_group)
        
        self.tab_widget.addTab(info_widget, "Information")
        
    def create_members_tab(self):
        """Create the group members tab"""
        members_widget = QWidget()
        members_layout = QVBoxLayout(members_widget)
        
        # Members table
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(5)
        self.members_table.setHorizontalHeaderLabels(["Name", "Username", "Email", "Role", "Last Access"])
        
        # Set table properties
        header = self.members_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.members_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.members_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.members_table.setAlternatingRowColors(True)
        
        members_layout.addWidget(self.members_table)
        
        self.tab_widget.addTab(members_widget, "Members")
        
    def setup_actions(self):
        """Setup actions and signals"""
        # Connect table double click
        self.members_table.doubleClicked.connect(self.on_member_double_clicked)
        
    def set_group(self, group: IUsersGroup, course: Optional[ICourse] = None):
        """Set the group and update the form"""
        self.group = group
        self.course = course
        
        if group:
            self.setWindowTitle(f"Users Group: {group.name}")
            self.update_group_info()
            self.update_members_table()
            self.update_button_states()
        else:
            self.setWindowTitle("Users Group Information")
            self.clear_form()
            
    def update_group_info(self):
        """Update group information fields"""
        if not self.group:
            return
            
        self.id_label.setText(str(self.group.id))
        self.name_edit.setText(self.group.name or "")
        self.description_edit.setText(self.group.description or "")
        self.id_number_edit.setText(self.group.id_number or "")
        self.enrolment_key_edit.setText(self.group.enrolment_key or "")
        self.picture_edit.setText(self.group.picture or "")
        self.time_created_edit.setText(self.group.time_created or "")
        self.time_modified_edit.setText(self.group.time_modified or "")
        self.notes_edit.setText(self.group.notes or "")
        
    def update_members_table(self):
        """Update the members table"""
        self.members_table.setRowCount(0)
        
        if not self.group:
            return
            
        # This would typically load group members from the LMS
        # For now, we'll show a placeholder
        # In a real implementation, you would get the group's members
        pass
        
    def update_button_states(self):
        """Update button enabled states"""
        enabled = self.group is not None
        self.refresh_button.setEnabled(enabled)
        
    def refresh_data(self):
        """Refresh group data"""
        if self.group:
            self.update_group_info()
            self.update_members_table()
            
    def on_member_double_clicked(self, index):
        """Handle member double click"""
        # This would typically open a user form
        pass
        
    def clear_form(self):
        """Clear all form fields"""
        self.id_label.setText("")
        self.name_edit.setText("")
        self.description_edit.setText("")
        self.id_number_edit.setText("")
        self.enrolment_key_edit.setText("")
        self.picture_edit.setText("")
        self.time_created_edit.setText("")
        self.time_modified_edit.setText("")
        self.notes_edit.setText("")
        self.members_table.setRowCount(0)
        
    def closeEvent(self, event):
        """Handle form close event"""
        # Clean up resources
        self.clear_form()
        super().closeEvent(event)
