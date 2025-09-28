"""
Course Content Tree Widget
Tree view for displaying course content (sections, modules, and files)
"""

from typing import Optional, List
from PyQt5.QtWidgets import QTreeWidgetItem, QMenu, QAction, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import ICourse, ISection, IModule, IContent
from tree_views.custom_tree import CustomTreeWidget, TreeData, NodeTypes
from helpers.browser import BrowserHelper


class CourseContentTreeWidget(CustomTreeWidget):
    """Tree widget for displaying course content"""
    
    # Signals
    content_selected = pyqtSignal(object)  # Emitted when content is selected
    content_double_clicked = pyqtSignal(object)  # Emitted when content is double-clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.course: Optional[ICourse] = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the tree widget UI"""
        # Set header labels
        self.setHeaderLabels(["Section", "Module", "Content", "File"])
        
        # Set column properties
        header = self.header()
        header.setStretchLastSection(False)
        for i in range(4):
            header.setSectionResizeMode(i, header.Stretch)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.item_double_clicked.connect(self.on_item_double_clicked)
        
    def set_course(self, course: ICourse):
        """Set the course and populate the tree"""
        self.course = course
        self.populate_tree()
        
    def populate_tree(self):
        """Populate the tree with course content data"""
        self.clear()
        
        if not self.course:
            return
            
        for section in self.course.sections:
            self.add_section_item(section)
            
        # Auto-resize columns
        self.header().resizeSections(QHeaderView.ResizeToContents)
        
    def add_section_item(self, section: ISection) -> QTreeWidgetItem:
        """Add a section item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.SECTION
        data.section = section
        
        item = QTreeWidgetItem(self)
        item.setText(0, section.name or f"Section {section.id}")
        item.setText(1, "")  # Empty for section
        item.setText(2, "")  # Empty for section
        item.setText(3, "")  # Empty for section
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon
        self.set_item_icon(item, NodeTypes.SECTION)
        
        # Add modules in this section
        for module in section.modules:
            self.add_module_item(module, item)
            
        # Expand the section item
        item.setExpanded(True)
        
        return item
        
    def add_module_item(self, module: IModule, parent: QTreeWidgetItem) -> QTreeWidgetItem:
        """Add a module item to the tree"""
        data = TreeData()
        data.module = module
        
        if len(module.contents) == 1:
            # Single content module
            data.node_type = NodeTypes.MODULE_ONE
            content = module.contents[0]
            
            item = QTreeWidgetItem(parent)
            item.setText(1, module.name or f"Module {module.id}")
            item.setText(2, content.mime_type or "")
            item.setText(3, content.file_url or "")
            
        else:
            # Multiple content module
            data.node_type = NodeTypes.MODULE
            
            item = QTreeWidgetItem(parent)
            item.setText(1, module.name or f"Module {module.id}")
            item.setText(2, "")  # Empty for module
            item.setText(3, "")  # Empty for module
            
            # Add contents in this module
            for content in module.contents:
                self.add_content_item(content, item)
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon based on module type
        self.set_module_icon(item, module)
        
        return item
        
    def add_content_item(self, content: IContent, parent: QTreeWidgetItem) -> QTreeWidgetItem:
        """Add a content item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.CONTENT
        data.content = content
        
        item = QTreeWidgetItem(parent)
        item.setText(2, content.mime_type or "")
        item.setText(3, content.file_url or "")
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon based on content type
        self.set_content_icon(item, content)
        
        return item
        
    def set_module_icon(self, item: QTreeWidgetItem, module: IModule):
        """Set the appropriate icon for a module based on its type"""
        icon_name = ""
        
        if module.mod_name:
            mod_name_lower = module.mod_name.lower()
            if "resource" in mod_name_lower or "file" in mod_name_lower:
                icon_name = "res_modtype_pdf"
            elif "label" in mod_name_lower:
                icon_name = "res_modtype_label"
            elif "folder" in mod_name_lower:
                icon_name = "res_modtype_folder"
            elif "forum" in mod_name_lower:
                icon_name = "res_modtype_forum"
            else:
                icon_name = "res_modtype_resource"
        else:
            icon_name = "res_modtype_resource"
            
        icon = self.image_helper.get_icon(icon_name)
        if icon:
            item.setIcon(1, icon)
            
    def set_content_icon(self, item: QTreeWidgetItem, content: IContent):
        """Set the appropriate icon for content based on its MIME type"""
        if content.file_type == "file":
            icon = self.image_helper.get_icon_by_mime_type(content.mime_type)
        elif content.file_type == "url":
            icon = self.image_helper.get_icon("res_modtype_url")
        else:
            icon = self.image_helper.get_icon("res_modtype_resource")
            
        if icon:
            item.setIcon(2, icon)
            
    def get_selected_content(self) -> Optional[IContent]:
        """Get the selected content"""
        data = self.get_selected_item_data()
        if data and data.node_type == NodeTypes.CONTENT:
            return data.content
        return None
        
    def get_selected_module(self) -> Optional[IModule]:
        """Get the selected module"""
        data = self.get_selected_item_data()
        if data and data.node_type in [NodeTypes.MODULE, NodeTypes.MODULE_ONE]:
            return data.module
        return None
        
    def filter_by_text(self, filter_text: str):
        """Filter items by text"""
        if not filter_text:
            self.show_all_items()
            return
            
        filter_text = filter_text.lower()
        self._filter_recursive(self.invisibleRootItem(), filter_text)
        
    def _filter_recursive(self, item: QTreeWidgetItem, filter_text: str):
        """Recursively filter items"""
        data = self.get_item_data(item)
        should_show = False
        
        if data:
            # Check if this item matches the filter
            compare_text = ""
            if data.node_type == NodeTypes.SECTION and data.section:
                compare_text = data.section.name
            elif data.node_type in [NodeTypes.MODULE, NodeTypes.MODULE_ONE] and data.module:
                compare_text = data.module.name
            elif data.node_type == NodeTypes.CONTENT and data.content:
                compare_text = data.content.filter_content
                
            if filter_text in compare_text.lower():
                should_show = True
                
        # Check children
        has_visible_child = False
        for i in range(item.childCount()):
            child = item.child(i)
            self._filter_recursive(child, filter_text)
            if not child.isHidden():
                has_visible_child = True
                
        # Show item if it matches or has visible children
        item.setHidden(not (should_show or has_visible_child))
        
    def show_only_resources(self):
        """Show only resource modules (files)"""
        for i in range(self.topLevelItemCount()):
            section_item = self.topLevelItem(i)
            self._show_only_resources_recursive(section_item)
            
    def _show_only_resources_recursive(self, item: QTreeWidgetItem):
        """Recursively show only resource modules"""
        data = self.get_item_data(item)
        should_show = False
        
        if data:
            if data.node_type == NodeTypes.SECTION:
                should_show = True
            elif data.node_type == NodeTypes.MODULE_ONE and data.module:
                # Show single-content modules
                should_show = True
                
        # Check children
        has_visible_child = False
        for i in range(item.childCount()):
            child = item.child(i)
            self._show_only_resources_recursive(child)
            if not child.isHidden():
                has_visible_child = True
                
        # Show item if it should be shown or has visible children
        item.setHidden(not (should_show or has_visible_child))
        
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        data = self.get_item_data(item)
        if data:
            if data.node_type == NodeTypes.CONTENT:
                self.content_selected.emit(data.content)
                
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click"""
        data = self.get_item_data(item)
        if data:
            if data.node_type == NodeTypes.CONTENT:
                self.content_double_clicked.emit(data.content)
            elif data.node_type == NodeTypes.MODULE_ONE and data.module and len(data.module.contents) == 1:
                # Open single content module
                self.content_double_clicked.emit(data.module.contents[0])
                
    def show_context_menu(self, position):
        """Show context menu for the selected item"""
        item = self.itemAt(position)
        if item:
            data = self.get_item_data(item)
            if data:
                menu = QMenu(self)
                
                if data.node_type == NodeTypes.CONTENT:
                    # Content context menu
                    open_action = QAction("Open File", self)
                    open_action.triggered.connect(lambda: self.open_content(data.content))
                    menu.addAction(open_action)
                    
                    if data.content.file_url:
                        open_browser_action = QAction("Open in Browser", self)
                        open_browser_action.triggered.connect(lambda: self.open_content_in_browser(data.content))
                        menu.addAction(open_browser_action)
                        
                elif data.node_type in [NodeTypes.MODULE, NodeTypes.MODULE_ONE]:
                    # Module context menu
                    if data.node_type == NodeTypes.MODULE_ONE and data.module and len(data.module.contents) == 1:
                        open_action = QAction("Open File", self)
                        open_action.triggered.connect(lambda: self.open_content(data.module.contents[0]))
                        menu.addAction(open_action)
                        
                menu.exec_(self.viewport().mapToGlobal(position))
                
    def open_content(self, content: IContent):
        """Open content file"""
        if content and content.file_url:
            BrowserHelper.open_url(content.file_url)
            
    def open_content_in_browser(self, content: IContent):
        """Open content in browser"""
        if content and content.file_url:
            BrowserHelper.open_url(content.file_url)
            
    def refresh(self):
        """Refresh the tree"""
        self.populate_tree()
        
    def clear_course(self):
        """Clear the course from the tree"""
        self.clear()
        self.course = None
