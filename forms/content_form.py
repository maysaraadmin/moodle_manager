"""
Content Form
Form for displaying content information and details
"""

from typing import Optional
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QGroupBox,
                             QFormLayout, QTabWidget, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import IContent, ICourse, IModule, ISection
from helpers.browser import BrowserHelper


class ContentForm(QDialog):
    """Form for displaying content information and details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.content: Optional[IContent] = None
        self.course: Optional[ICourse] = None
        self.module: Optional[IModule] = None
        self.section: Optional[ISection] = None
        
        self.setup_ui()
        self.setup_actions()
        
    def setup_ui(self):
        """Setup the form UI"""
        self.setWindowTitle("Content Information")
        self.resize(600, 500)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create info tab
        self.create_info_tab()
        
        # Create preview tab
        self.create_preview_tab()
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Add buttons
        self.open_in_browser_button = QPushButton("Open in Browser")
        self.open_in_browser_button.clicked.connect(self.open_in_browser)
        button_layout.addWidget(self.open_in_browser_button)
        
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_content)
        button_layout.addWidget(self.download_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
        
    def create_info_tab(self):
        """Create the content information tab"""
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
        
        self.filename_edit = QLineEdit()
        self.filename_edit.setReadOnly(True)
        basic_layout.addRow("Filename:", self.filename_edit)
        
        self.filepath_edit = QLineEdit()
        self.filepath_edit.setReadOnly(True)
        basic_layout.addRow("Filepath:", self.filepath_edit)
        
        self.fileurl_edit = QLineEdit()
        self.fileurl_edit.setReadOnly(True)
        basic_layout.addRow("File URL:", self.fileurl_edit)
        
        info_layout.addWidget(basic_group)
        
        # File information group
        file_group = QGroupBox("File Information")
        file_layout = QFormLayout(file_group)
        
        self.mimetype_edit = QLineEdit()
        self.mimetype_edit.setReadOnly(True)
        file_layout.addRow("MIME Type:", self.mimetype_edit)
        
        self.size_edit = QLineEdit()
        self.size_edit.setReadOnly(True)
        file_layout.addRow("Size:", self.size_edit)
        
        self.time_created_edit = QLineEdit()
        self.time_created_edit.setReadOnly(True)
        file_layout.addRow("Time Created:", self.time_created_edit)
        
        self.time_modified_edit = QLineEdit()
        self.time_modified_edit.setReadOnly(True)
        file_layout.addRow("Time Modified:", self.time_modified_edit)
        
        info_layout.addWidget(file_group)
        
        # Status information group
        status_group = QGroupBox("Status Information")
        status_layout = QFormLayout(status_group)
        
        self.visible_edit = QLineEdit()
        self.visible_edit.setReadOnly(True)
        status_layout.addRow("Visible:", self.visible_edit)
        
        self.status_edit = QLineEdit()
        self.status_edit.setReadOnly(True)
        status_layout.addRow("Status:", self.status_edit)
        
        self.sort_order_edit = QLineEdit()
        self.sort_order_edit.setReadOnly(True)
        status_layout.addRow("Sort Order:", self.sort_order_edit)
        
        info_layout.addWidget(status_group)
        
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
        
    def create_preview_tab(self):
        """Create the content preview tab"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # Preview area
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setPlaceholderText("Content preview will be displayed here...")
        preview_layout.addWidget(self.preview_edit)
        
        self.tab_widget.addTab(preview_widget, "Preview")
        
    def setup_actions(self):
        """Setup actions and signals"""
        pass
        
    def set_content(self, content: IContent, course: Optional[ICourse] = None, 
                   module: Optional[IModule] = None, section: Optional[ISection] = None):
        """Set the content and update the form"""
        self.content = content
        self.course = course
        self.module = module
        self.section = section
        
        if content:
            self.setWindowTitle(f"Content: {content.name}")
            self.update_content_info()
            self.update_preview()
            self.update_button_states()
        else:
            self.setWindowTitle("Content Information")
            self.clear_form()
            
    def update_content_info(self):
        """Update content information fields"""
        if not self.content:
            return
            
        self.id_label.setText(str(self.content.id))
        self.name_edit.setText(self.content.name or "")
        self.filename_edit.setText(self.content.filename or "")
        self.filepath_edit.setText(self.content.filepath or "")
        self.fileurl_edit.setText(self.content.fileurl or "")
        self.mimetype_edit.setText(self.content.mimetype or "")
        self.size_edit.setText(self.format_file_size(self.content.size) if self.content.size else "")
        self.time_created_edit.setText(self.content.time_created or "")
        self.time_modified_edit.setText(self.content.time_modified or "")
        self.visible_edit.setText(str(self.content.visible) if self.content.visible is not None else "")
        self.status_edit.setText(self.content.status or "")
        self.sort_order_edit.setText(str(self.content.sort_order) if self.content.sort_order is not None else "")
        self.description_edit.setText(self.content.description or "")
        self.notes_edit.setText(self.content.notes or "")
        
    def update_preview(self):
        """Update the content preview"""
        if not self.content:
            self.preview_edit.clear()
            return
            
        # This would typically load and display content preview
        # For now, we'll show a placeholder
        if self.content.mimetype and self.content.mimetype.startswith("text/"):
            # For text files, we could load the content
            self.preview_edit.setText("Text content preview would be displayed here...")
        elif self.content.mimetype and self.content.mimetype.startswith("image/"):
            # For images, we could show the image
            self.preview_edit.setText("Image preview would be displayed here...")
        else:
            # For other file types
            self.preview_edit.setText("Preview not available for this file type.")
            
    def update_button_states(self):
        """Update button enabled states"""
        enabled = self.content is not None
        self.open_in_browser_button.setEnabled(enabled and self.content.fileurl is not None)
        self.download_button.setEnabled(enabled and self.content.fileurl is not None)
        
    def open_in_browser(self):
        """Open content in browser"""
        if self.content and self.content.fileurl:
            BrowserHelper.open_url(self.content.fileurl)
            
    def download_content(self):
        """Download content"""
        if self.content and self.content.fileurl:
            # This would typically download the content
            pass
            
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if not size_bytes:
            return ""
            
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
        
    def clear_form(self):
        """Clear all form fields"""
        self.id_label.setText("")
        self.name_edit.setText("")
        self.filename_edit.setText("")
        self.filepath_edit.setText("")
        self.fileurl_edit.setText("")
        self.mimetype_edit.setText("")
        self.size_edit.setText("")
        self.time_created_edit.setText("")
        self.time_modified_edit.setText("")
        self.visible_edit.setText("")
        self.status_edit.setText("")
        self.sort_order_edit.setText("")
        self.description_edit.setText("")
        self.notes_edit.setText("")
        self.preview_edit.clear()
        
    def closeEvent(self, event):
        """Handle form close event"""
        # Clean up resources
        self.clear_form()
        super().closeEvent(event)
