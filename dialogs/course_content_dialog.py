"""
Course Content Dialog for LMS Explorer
Dialog to display course content (sections, modules, and files)
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, 
                             QSplitter, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt
from lms_interface import ICourse, ISection, IModule, IContent


class CourseContentDialog(QDialog):
    """Dialog to display course content"""
    
    def __init__(self, course: ICourse, parent=None):
        super().__init__(parent)
        
        self.course = course
        self.setWindowTitle(f"Course Content - {course.fullname or course.shortname}")
        self.setModal(True)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.setup_ui()
        self.load_content()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(f"Course: {self.course.fullname or self.course.shortname}")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Content tree
        self.content_tree = QTreeWidget()
        self.content_tree.setHeaderLabels(["Section", "Module", "Content"])
        self.content_tree.itemClicked.connect(self.on_item_clicked)
        splitter.addWidget(self.content_tree)
        
        # Right side - Details
        right_widget = QVBoxLayout()
        
        # Details label
        self.details_label = QLabel("Select an item to view details")
        self.details_label.setStyleSheet("font-weight: bold; margin: 5px;")
        right_widget.addWidget(self.details_label)
        
        # Details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_widget.addWidget(self.details_text)
        
        # Add right widget to splitter
        right_container = QWidget()
        right_container.setLayout(right_widget)
        splitter.addWidget(right_container)
        
        # Set splitter sizes
        splitter.setSizes([400, 400])
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_content)
        button_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def load_content(self):
        """Load course content"""
        self.content_tree.clear()
        self.details_text.clear()
        self.details_label.setText("Select an item to view details")
        
        try:
            # Get course content
            content = self.course.get_course_content()
            
            if not content:
                self.details_label.setText("No content found")
                self.details_text.setText("This course has no content available.")
                return
            
            # Add sections to tree
            for section in content:
                section_item = QTreeWidgetItem(self.content_tree)
                section_item.setText(0, section.name or f"Section {section.id}")
                section_item.setText(1, "")
                section_item.setText(2, "")
                
                # Store section data
                section_item.setData(0, Qt.UserRole, section)
                
                # Add modules to section
                for module in section.get_modules():
                    module_item = QTreeWidgetItem(section_item)
                    module_item.setText(0, "")
                    module_item.setText(1, module.name or f"Module {module.id}")
                    module_item.setText(2, "")
                    
                    # Store module data
                    module_item.setData(0, Qt.UserRole, module)
                    
                    # Add content to module
                    for content_item in module.get_contents():
                        content_item_tree = QTreeWidgetItem(module_item)
                        content_item_tree.setText(0, "")
                        content_item_tree.setText(1, "")
                        content_item_tree.setText(2, content_item.get_file_name() or "File")
                        
                        # Store content data
                        content_item_tree.setData(0, Qt.UserRole, content_item)
            
            # Expand all sections
            self.content_tree.expandAll()
            
            # Resize columns
            self.content_tree.header().resizeSections(QTreeWidget.ResizeToContents)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load course content: {str(e)}")
            
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click in the content tree"""
        data = item.data(0, Qt.UserRole)
        
        if not data:
            return
            
        if isinstance(data, ISection):
            self.show_section_details(data)
        elif isinstance(data, IModule):
            self.show_module_details(data)
        elif isinstance(data, IContent):
            self.show_content_details(data)
            
    def show_section_details(self, section: ISection):
        """Show section details"""
        self.details_label.setText(f"Section: {section.name or f'Section {section.id}'}")
        
        details = f"Section ID: {section.id}\n"
        details += f"Name: {section.name or 'N/A'}\n"
        details += f"Course: {section.get_course().fullname if section.get_course() else 'N/A'}\n"
        details += f"Number of Modules: {len(section.get_modules())}\n"
        
        self.details_text.setText(details)
        
    def show_module_details(self, module: IModule):
        """Show module details"""
        self.details_label.setText(f"Module: {module.name or f'Module {module.id}'}")
        
        details = f"Module ID: {module.id}\n"
        details += f"Name: {module.name or 'N/A'}\n"
        details += f"Type: {module.mod_name or 'N/A'}\n"
        details += f"Section: {module.get_section().name if module.get_section() else 'N/A'}\n"
        details += f"Number of Content Items: {len(module.get_contents())}\n"
        
        self.details_text.setText(details)
        
    def show_content_details(self, content: IContent):
        """Show content details"""
        self.details_label.setText(f"Content: {content.get_file_name() or 'File'}")
        
        details = f"File Name: {content.get_file_name() or 'N/A'}\n"
        details += f"File Type: {content.get_file_type() or 'N/A'}\n"
        details += f"MIME Type: {content.get_mime_type() or 'N/A'}\n"
        details += f"File URL: {content.get_file_url() or 'N/A'}\n"
        details += f"Module: {content.get_module().name if content.get_module() else 'N/A'}\n"
        
        self.details_text.setText(details)
