"""
Course Users Tree Widget
Tree view for displaying users in a specific course
"""

from typing import Optional, List
from PyQt5.QtWidgets import QTreeWidgetItem, QMenu, QAction, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import ICourse, IUser, IUsersGroup
from tree_views.custom_tree import CustomTreeWidget, TreeData, NodeTypes
from helpers.browser import BrowserHelper


class CourseUsersTreeWidget(CustomTreeWidget):
    """Tree widget for displaying users in a specific course"""
    
    # Signals
    user_selected = pyqtSignal(object)  # Emitted when a user is selected
    user_double_clicked = pyqtSignal(object)  # Emitted when a user is double-clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.course: Optional[ICourse] = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the tree widget UI"""
        # Set header labels
        self.setHeaderLabels(["Full Name", "First Name", "Last Name", "Email", "Roles", "Last Access", "Last Access From"])
        
        # Set column properties
        header = self.header()
        header.setStretchLastSection(False)
        for i in range(7):
            header.setSectionResizeMode(i, header.Stretch)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.item_double_clicked.connect(self.on_item_double_clicked)
        
    def set_course(self, course: ICourse):
        """Set the course and populate the tree"""
        self.course = course
        self.populate_tree()
        
    def populate_tree(self):
        """Populate the tree with course users data"""
        self.clear()
        
        if not self.course:
            return
            
        # Refresh enrolled users
        self.course.refresh_enrolled_users()
        
        # Check if course has groups
        if self.course.user_groups and len(self.course.user_groups) > 0:
            # Show groups structure
            self.setHeaderLabels(["Group", "Full Name", "First Name", "Last Name", "Email", "Roles", "Last Access", "Last Access From"])
            
            for group in self.course.user_groups:
                self.add_group_item(group)
        else:
            # Show flat users list
            self.setHeaderLabels(["Full Name", "First Name", "Last Name", "Email", "Roles", "Last Access", "Last Access From"])
            
            for user in self.course.users:
                self.add_user_item(user)
                
        # Auto-resize columns
        self.header().resizeSections(QHeaderView.ResizeToContents)
        
    def add_group_item(self, group: IUsersGroup) -> QTreeWidgetItem:
        """Add a group item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.GROUP
        data.group = group
        
        item = QTreeWidgetItem(self)
        item.setText(0, group.group_name or f"Group {group.id}")
        item.setText(1, "")  # Empty for group
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon
        self.set_item_icon(item, NodeTypes.GROUP)
        
        # Add users in this group
        for user in group.users_in_group:
            self.add_user_item(user, item)
            
        # Expand the group item
        item.setExpanded(True)
        
        return item
        
    def add_user_item(self, user: IUser, parent: Optional[QTreeWidgetItem] = None) -> QTreeWidgetItem:
        """Add a user item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.USER
        data.user = user
        
        if parent:
            item = QTreeWidgetItem(parent)
            # For grouped users, start from column 1
            item.setText(1, user.full_name or f"User {user.id}")
            item.setText(2, user.first_name or "")
            item.setText(3, user.last_name or "")
            item.setText(4, user.email or "")
            item.setText(5, user.roles or "")
            item.setText(6, user.last_access or "")
            item.setText(7, user.last_access_from or "")
        else:
            item = QTreeWidgetItem(self)
            # For flat users, start from column 0
            item.setText(0, user.full_name or f"User {user.id}")
            item.setText(1, user.first_name or "")
            item.setText(2, user.last_name or "")
            item.setText(3, user.email or "")
            item.setText(4, user.roles or "")
            item.setText(5, user.last_access or "")
            item.setText(6, user.last_access_from or "")
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon
        self.set_item_icon(item, NodeTypes.USER)
        
        return item
        
    def get_selected_user(self) -> Optional[IUser]:
        """Get the selected user"""
        data = self.get_selected_item_data()
        if data and data.node_type == NodeTypes.USER:
            return data.user
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
            if data.node_type == NodeTypes.GROUP and data.group:
                compare_text = data.group.filter_content
            elif data.node_type == NodeTypes.USER and data.user:
                compare_text = data.user.filter_content
                
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
        if data and data.node_type == NodeTypes.USER:
            self.user_selected.emit(data.user)
            
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click"""
        data = self.get_item_data(item)
        if data and data.node_type == NodeTypes.USER:
            self.user_double_clicked.emit(data.user)
            
    def show_context_menu(self, position):
        """Show context menu for the selected item"""
        item = self.itemAt(position)
        if item:
            data = self.get_item_data(item)
            if data and data.node_type == NodeTypes.USER:
                menu = QMenu(self)
                
                # Add context menu actions
                view_profile_action = QAction("View Profile", self)
                view_profile_action.triggered.connect(lambda: self.view_user_profile(data.user))
                menu.addAction(view_profile_action)
                
                view_grades_action = QAction("View Grades", self)
                view_grades_action.triggered.connect(lambda: self.view_user_grades(data.user))
                menu.addAction(view_grades_action)
                
                menu.addSeparator()
                
                open_browser_action = QAction("Open in Browser", self)
                open_browser_action.triggered.connect(lambda: self.open_user_in_browser(data.user))
                menu.addAction(open_browser_action)
                
                menu.exec_(self.viewport().mapToGlobal(position))
                
    def view_user_profile(self, user: IUser):
        """View user profile"""
        self.user_double_clicked.emit(user)
        
    def view_user_grades(self, user: IUser):
        """View user grades"""
        pass
        
    def open_user_in_browser(self, user: IUser):
        """Open user profile in browser"""
        if user and self.course:
            BrowserHelper.open_user_profile(self.course, user)
            
    def refresh(self):
        """Refresh the tree"""
        self.populate_tree()
        
    def clear_course(self):
        """Clear the course from the tree"""
        self.clear()
        self.course = None
