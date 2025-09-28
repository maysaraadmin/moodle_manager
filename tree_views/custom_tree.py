"""
Custom Tree Widget Base Class
Base class for all LMS tree widgets with common functionality
"""

from enum import Enum
from typing import Optional, Any, List
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon

from lms_interface import ILMS, ICourse, ICategory, IUser, IUsersGroup, ISection, IModule, IContent
from helpers.images import ImageHelper


class NodeTypes(Enum):
    """Enumeration of different node types in the tree"""
    LMS = "lms"
    CATEGORY = "category"
    COURSE = "course"
    GROUP = "group"
    USER = "user"
    SECTION = "section"
    MODULE = "module"
    MODULE_ONE = "module_one"
    CONTENT = "content"


class TreeData:
    """Data structure for tree node data"""
    
    def __init__(self):
        self.node_type: Optional[NodeTypes] = None
        self.lms: Optional[ILMS] = None
        self.course: Optional[ICourse] = None
        self.user: Optional[IUser] = None
        self.category: Optional[ICategory] = None
        self.group: Optional[IUsersGroup] = None
        self.section: Optional[ISection] = None
        self.module: Optional[IModule] = None
        self.content: Optional[IContent] = None


class CustomTreeWidget(QTreeWidget):
    """Base class for all LMS tree widgets"""
    
    # Signals
    item_double_clicked = pyqtSignal(object)  # Emitted when an item is double-clicked
    context_menu_requested = pyqtSignal(object, object)  # Emitted when context menu is requested
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.image_helper = ImageHelper()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the tree widget UI"""
        # Set basic properties
        self.setHeaderLabels(["Name", "ID", "Type"])
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Connect signals
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Set selection mode
        self.setSelectionMode(QTreeWidget.SingleSelection)
        
        # Enable drag and drop if needed
        self.setDragDropMode(QTreeWidget.NoDragDrop)
        
        # Set alternating row colors
        self.setAlternatingRowColors(True)
        
        # Set column properties
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, header.Stretch)
        
    def create_tree_item(self, parent: QTreeWidgetItem, data: TreeData, 
                        name: str, id_text: str = "", type_text: str = "") -> QTreeWidgetItem:
        """Create a tree item with the given data"""
        item = QTreeWidgetItem(parent)
        item.setText(0, name)
        item.setText(1, id_text)
        item.setText(2, type_text)
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon based on node type
        self.set_item_icon(item, data.node_type)
        
        return item
        
    def set_item_icon(self, item: QTreeWidgetItem, node_type: NodeTypes):
        """Set the appropriate icon for a tree item based on its type"""
        icon_map = {
            NodeTypes.LMS: "res_lms",
            NodeTypes.COURSE: "res_course",
            NodeTypes.CATEGORY: "res_category",
            NodeTypes.USER: "res_user",
            NodeTypes.GROUP: "res_group",
            NodeTypes.SECTION: "res_section",
            NodeTypes.MODULE: "res_module",
            NodeTypes.CONTENT: "res_content",
        }
        
        if node_type in icon_map:
            icon = self.image_helper.get_icon(icon_map[node_type])
            if icon:
                item.setIcon(0, icon)
                
    def get_item_data(self, item: QTreeWidgetItem) -> Optional[TreeData]:
        """Get the data object from a tree item"""
        if item:
            return item.data(0, Qt.UserRole)
        return None
        
    def get_selected_item_data(self) -> Optional[TreeData]:
        """Get the data object from the selected item"""
        selected_items = self.selectedItems()
        if selected_items:
            return self.get_item_data(selected_items[0])
        return None
        
    def filter_items(self, filter_text: str):
        """Filter tree items based on the filter text"""
        if not filter_text:
            # Show all items
            self.show_all_items()
            return
            
        filter_text = filter_text.lower()
        self._filter_recursive(self.invisibleRootItem(), filter_text)
        
    def show_all_items(self):
        """Show all items in the tree"""
        self._show_recursive(self.invisibleRootItem())
        
    def hide_all_items(self):
        """Hide all items in the tree"""
        self._hide_recursive(self.invisibleRootItem())
        
    def _show_recursive(self, item: QTreeWidgetItem):
        """Recursively show items"""
        item.setHidden(False)
        for i in range(item.childCount()):
            self._show_recursive(item.child(i))
            
    def _hide_recursive(self, item: QTreeWidgetItem):
        """Recursively hide items"""
        item.setHidden(True)
        for i in range(item.childCount()):
            self._hide_recursive(item.child(i))
            
    def _filter_recursive(self, item: QTreeWidgetItem, filter_text: str):
        """Recursively filter items"""
        data = self.get_item_data(item)
        should_show = False
        
        if data:
            # Check if this item matches the filter
            compare_text = ""
            if data.node_type == NodeTypes.LMS and data.lms:
                compare_text = f"{data.lms.name} {data.lms.host}"
            elif data.node_type == NodeTypes.CATEGORY and data.category:
                compare_text = data.category.name
            elif data.node_type == NodeTypes.COURSE and data.course:
                compare_text = data.course.filter_content
            elif data.node_type == NodeTypes.USER and data.user:
                compare_text = data.user.filter_content
            elif data.node_type == NodeTypes.GROUP and data.group:
                compare_text = data.group.filter_content
                
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
        
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click"""
        data = self.get_item_data(item)
        if data:
            self.item_double_clicked.emit(data)
            
    def show_context_menu(self, position):
        """Show context menu for the selected item"""
        item = self.itemAt(position)
        if item:
            data = self.get_item_data(item)
            if data:
                self.context_menu_requested.emit(data, position)
                
    def handle_context_menu_action(self, action, data, item):
        """Handle context menu action - to be overridden by subclasses"""
        pass
        
    def refresh_item(self, item: QTreeWidgetItem):
        """Refresh a specific item - to be overridden by subclasses"""
        pass
        
    def get_all_items(self) -> List[QTreeWidgetItem]:
        """Get all items in the tree"""
        items = []
        self._collect_items_recursive(self.invisibleRootItem(), items)
        return items
        
    def _collect_items_recursive(self, item: QTreeWidgetItem, items: List[QTreeWidgetItem]):
        """Recursively collect all items"""
        for i in range(item.childCount()):
            child = item.child(i)
            items.append(child)
            self._collect_items_recursive(child, items)
            
    def expand_all(self):
        """Expand all items in the tree"""
        self.expand_recursive(self.invisibleRootItem())
        
    def collapse_all(self):
        """Collapse all items in the tree"""
        self.collapse_recursive(self.invisibleRootItem())
        
    def expand_recursive(self, item: QTreeWidgetItem):
        """Recursively expand items"""
        item.setExpanded(True)
        for i in range(item.childCount()):
            self.expand_recursive(item.child(i))
            
    def collapse_recursive(self, item: QTreeWidgetItem):
        """Recursively collapse items"""
        item.setExpanded(False)
        for i in range(item.childCount()):
            self.collapse_recursive(item.child(i))
