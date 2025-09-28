"""
Course Category Tree Widget
Tree view for displaying courses in a specific category
"""

from typing import Optional, List
from PyQt5.QtWidgets import QTreeWidgetItem, QMenu, QAction, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import ICategory, ICourse, IUser, IUsersGroup
from tree_views.custom_tree import CustomTreeWidget, TreeData, NodeTypes
from helpers.browser import BrowserHelper


class CourseCategoryTreeWidget(CustomTreeWidget):
    """Tree widget for displaying courses in a specific category"""
    
    # Signals
    user_selected = pyqtSignal(object)  # Emitted when a user is selected
    course_selected = pyqtSignal(object)  # Emitted when a course is selected
    course_double_clicked = pyqtSignal(object)  # Emitted when a course is double-clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.category: Optional[ICategory] = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the tree widget UI"""
        # Set header labels
        self.setHeaderLabels(["Course", "Group", "Full Name", "Email", "Roles", "Last Access"])
        
        # Set column properties
        header = self.header()
        header.setStretchLastSection(False)
        for i in range(6):
            header.setSectionResizeMode(i, header.Stretch)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.item_double_clicked.connect(self.on_item_double_clicked)
        
    def set_category(self, category: ICategory):
        """Set the category and populate the tree"""
        self.category = category
        self.populate_tree()
        
    def populate_tree(self):
        """Populate the tree with category courses data"""
        self.clear()
        
        if not self.category:
            return
            
        for course in self.category.courses:
            self.add_course_item(course)
            
        # Auto-resize columns
        self.header().resizeSections(QHeaderView.ResizeToContents)
        
    def add_course_item(self, course: ICourse) -> QTreeWidgetItem:
        """Add a course item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.COURSE
        data.course = course
        
        item = QTreeWidgetItem(self)
        item.setText(0, course.displayname or f"Course {course.id}")
        item.setText(1, "")  # Empty for course
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon
        self.set_course_icon(item, course)
        
        # Refresh enrolled users for this course
        course.refresh_enrolled_users()
        
        # Add groups or users to this course
        if course.user_groups and len(course.user_groups) > 0:
            # Add groups
            for group in course.user_groups:
                self.add_group_item(group, item)
        elif course.users and len(course.users) > 0:
            # Add users directly
            for user in course.users:
                self.add_user_item(user, item)
                
        # Expand the course item
        item.setExpanded(True)
        
        return item
        
    def add_group_item(self, group: IUsersGroup, parent: QTreeWidgetItem) -> QTreeWidgetItem:
        """Add a group item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.GROUP
        data.group = group
        
        item = QTreeWidgetItem(parent)
        item.setText(1, group.group_name or f"Group {group.id}")
        
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
        
    def add_user_item(self, user: IUser, parent: QTreeWidgetItem) -> QTreeWidgetItem:
        """Add a user item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.USER
        data.user = user
        
        item = QTreeWidgetItem(parent)
        item.setText(2, user.full_name or f"User {user.id}")
        item.setText(3, user.email or "")
        item.setText(4, user.roles or "")
        item.setText(5, user.last_access or "")
        
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
            if data.node_type == NodeTypes.COURSE and data.course:
                compare_text = data.course.filter_content
            elif data.node_type == NodeTypes.GROUP and data.group:
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
        if data:
            if data.node_type == NodeTypes.USER:
                self.user_selected.emit(data.user)
            elif data.node_type == NodeTypes.COURSE:
                self.course_selected.emit(data.course)
                
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click"""
        data = self.get_item_data(item)
        if data and data.node_type == NodeTypes.COURSE:
            self.course_double_clicked.emit(data.course)
            
    def show_context_menu(self, position):
        """Show context menu for the selected item"""
        item = self.itemAt(position)
        if item:
            data = self.get_item_data(item)
            if data:
                menu = QMenu(self)
                
                if data.node_type == NodeTypes.COURSE:
                    # Course context menu
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
                    
                elif data.node_type == NodeTypes.USER:
                    # User context menu
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
                
    def view_course_content(self, course: ICourse):
        """View course content"""
        pass
        
    def view_course_users(self, course: ICourse):
        """View course users"""
        pass
        
    def open_course_in_browser(self, course: ICourse):
        """Open course in browser"""
        if course:
            BrowserHelper.open_course(course)
            
    def view_user_profile(self, user: IUser):
        """View user profile"""
        pass
        
    def view_user_grades(self, user: IUser):
        """View user grades"""
        pass
        
    def open_user_in_browser(self, user: IUser):
        """Open user profile in browser"""
        if user:
            # Find the course this user belongs to
            for course_item in self.get_course_items():
                course_data = self.get_item_data(course_item)
                if course_data and course_data.course:
                    BrowserHelper.open_user_profile(course_data.course, user)
                    break
                    
    def get_course_items(self) -> List[QTreeWidgetItem]:
        """Get all course items in the tree"""
        course_items = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = self.get_item_data(item)
            if data and data.node_type == NodeTypes.COURSE:
                course_items.append(item)
        return course_items
        
    def refresh(self):
        """Refresh the tree"""
        self.populate_tree()
        
    def clear_category(self):
        """Clear the category from the tree"""
        self.clear()
        self.category = None
