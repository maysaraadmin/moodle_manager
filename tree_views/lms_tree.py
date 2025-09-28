"""
LMS Tree Widget
Tree view for displaying LMS structure with categories and courses
"""

from typing import Optional, List
from PyQt5.QtWidgets import QTreeWidgetItem, QMenu, QAction, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor

from lms_interface import ILMS, ICategory, ICourse
from tree_views.custom_tree import CustomTreeWidget, TreeData, NodeTypes
from helpers.browser import BrowserHelper


class LMSTreeWidget(CustomTreeWidget):
    """Tree widget for displaying LMS structure"""
    
    # Signals
    category_selected = pyqtSignal(object)  # Emitted when a category is selected
    course_selected = pyqtSignal(object)  # Emitted when a course is selected
    category_double_clicked = pyqtSignal(object)  # Emitted when a category is double-clicked
    course_double_clicked = pyqtSignal(object)  # Emitted when a course is double-clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.lms: Optional[ILMS] = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the tree widget UI"""
        # Set header labels
        self.setHeaderLabels(["Name", "ID"])
        
        # Set column properties
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, header.Stretch)
        header.setSectionResizeMode(1, header.ResizeToContents)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
    def set_lms(self, lms: ILMS):
        """Set the LMS instance and populate the tree"""
        self.lms = lms
        self.populate_tree()
        
    def populate_tree(self):
        """Populate the tree with LMS data"""
        self.clear()
        
        if not self.lms:
            return
            
        # Get categories from connection
        self.lms.get_categories_from_connection()
        self.lms.get_courses()
        
        # Add first level categories
        for category in self.lms.first_level_categories:
            self.add_category_item(category)
            
        # Auto-resize columns
        self.header().resizeSections(QHeaderView.ResizeToContents)
        
    def add_category_item(self, category: ICategory, parent: Optional[QTreeWidgetItem] = None) -> QTreeWidgetItem:
        """Add a category item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.CATEGORY
        data.category = category
        
        if parent:
            item = QTreeWidgetItem(parent)
        else:
            item = QTreeWidgetItem(self)
            
        item.setText(0, category.name or f"Category {category.id}")
        item.setText(1, str(category.id))
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon
        self.set_item_icon(item, NodeTypes.CATEGORY)
        
        # Add subcategories
        for subcategory in category.categories:
            self.add_category_item(subcategory, item)
            
        # Add courses in this category
        for course in category.courses:
            self.add_course_item(course, item)
            
        # Expand if has children
        if (category.categories and len(category.categories) > 0) or \
           (category.courses and len(category.courses) > 0):
            item.setExpanded(True)
            
        return item
        
    def add_course_item(self, course: ICourse, parent: QTreeWidgetItem) -> QTreeWidgetItem:
        """Add a course item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.COURSE
        data.course = course
        
        item = QTreeWidgetItem(parent)
        item.setText(0, course.display_content or f"Course {course.id}")
        item.setText(1, str(course.id))
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon
        self.set_course_icon(item, course)
        
        return item
        
    def get_selected_category(self) -> Optional[ICategory]:
        """Get the selected category"""
        data = self.get_selected_item_data()
        if data and data.node_type == NodeTypes.CATEGORY:
            return data.category
        return None
        
    def get_selected_course(self) -> Optional[ICourse]:
        """Get the selected course"""
        data = self.get_selected_item_data()
        if data and data.node_type == NodeTypes.COURSE:
            return data.course
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
            if data.node_type == NodeTypes.CATEGORY and data.category:
                compare_text = data.category.name
            elif data.node_type == NodeTypes.COURSE and data.course:
                compare_text = data.course.filter_content
                
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
        
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        data = self.get_item_data(item)
        if data:
            if data.node_type == NodeTypes.CATEGORY:
                self.category_selected.emit(data.category)
            elif data.node_type == NodeTypes.COURSE:
                self.course_selected.emit(data.course)
                
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click"""
        data = self.get_item_data(item)
        if data:
            if data.node_type == NodeTypes.CATEGORY:
                self.category_double_clicked.emit(data.category)
            elif data.node_type == NodeTypes.COURSE:
                self.course_double_clicked.emit(data.course)
                
    def show_context_menu(self, position):
        """Show context menu for the selected item"""
        item = self.itemAt(position)
        if item:
            data = self.get_item_data(item)
            if data:
                menu = QMenu(self)
                
                if data.node_type == NodeTypes.CATEGORY:
                    # Category context menu
                    view_action = QAction("View Category", self)
                    view_action.triggered.connect(lambda: self.view_category(data.category))
                    menu.addAction(view_action)
                    
                    menu.addSeparator()
                    
                    open_browser_action = QAction("Open in Browser", self)
                    open_browser_action.triggered.connect(lambda: self.open_category_in_browser(data.category))
                    menu.addAction(open_browser_action)
                    
                elif data.node_type == NodeTypes.COURSE:
                    # Course context menu
                    view_action = QAction("View Course", self)
                    view_action.triggered.connect(lambda: self.view_course(data.course))
                    menu.addAction(view_action)
                    
                    view_content_action = QAction("View Content", self)
                    view_content_action.triggered.connect(lambda: self.view_course_content(data.course))
                    menu.addAction(view_content_action)
                    
                    view_users_action = QAction("View Users", self)
                    view_users_action.triggered.connect(lambda: self.view_course_users(data.course))
                    menu.addAction(view_users_action)
                    
                    menu.addSeparator()
                    
                    open_browser_action = QAction("Open in Browser", self)
                    open_browser_action.triggered.connect(lambda: self.open_course_in_browser(data.course))
                    menu.addAction(open_browser_action)
                    
                    open_users_browser_action = QAction("Open Users in Browser", self)
                    open_users_browser_action.triggered.connect(lambda: self.open_course_users_in_browser(data.course))
                    menu.addAction(open_users_browser_action)
                
                menu.exec_(self.viewport().mapToGlobal(position))
                
    def view_category(self, category: ICategory):
        """View category details"""
        self.category_double_clicked.emit(category)
        
    def view_course(self, course: ICourse):
        """View course details"""
        self.course_double_clicked.emit(course)
        
    def view_course_content(self, course: ICourse):
        """View course content"""
        pass
        
    def view_course_users(self, course: ICourse):
        """View course users"""
        pass
        
    def open_category_in_browser(self, category: ICategory):
        """Open category in browser"""
        if category and self.lms:
            BrowserHelper.open_category(self.lms, category)
            
    def open_course_in_browser(self, course: ICourse):
        """Open course in browser"""
        if course:
            BrowserHelper.open_course(course)
            
    def open_course_users_in_browser(self, course: ICourse):
        """Open course users in browser"""
        if course:
            BrowserHelper.open_course_users(course)
            
    def refresh(self):
        """Refresh the tree"""
        self.populate_tree()
        
    def clear_lms(self):
        """Clear the LMS from the tree"""
        self.clear()
        self.lms = None
