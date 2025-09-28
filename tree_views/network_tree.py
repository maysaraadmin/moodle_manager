"""
Network Tree Widget
Tree view for displaying LMS network structure
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import ILMS, ICourse, ICategory, IUser


class NetworkTreeWidget(QTreeWidget):
    """Tree widget for displaying LMS network structure"""
    
    # Signals
    item_selected = pyqtSignal(object)  # Emitted when an item is selected
    course_double_clicked = pyqtSignal(object)  # Emitted when a course is double-clicked
    user_double_clicked = pyqtSignal(object)  # Emitted when a user is double-clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.lms = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the tree widget UI"""
        # Set header labels
        self.setHeaderLabels(["Name", "ID", "Type"])
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Set selection mode
        self.setSelectionMode(QTreeWidget.SingleSelection)
        
        # Enable drag and drop if needed
        self.setDragDropMode(QTreeWidget.NoDragDrop)
        
    def set_lms(self, lms: ILMS):
        """Set the LMS instance and populate the tree"""
        self.lms = lms
        self.populate_tree()
        
    def populate_tree(self):
        """Populate the tree with LMS data"""
        self.clear()
        
        if not self.lms:
            return
            
        # Add LMS root item
        lms_item = QTreeWidgetItem(self)
        lms_item.setText(0, self.lms.name or "LMS")
        lms_item.setText(1, str(self.lms.host or ""))
        lms_item.setText(2, "LMS")
        lms_item.setData(0, Qt.UserRole, self.lms)
        
        # Add categories
        for category in self.lms.categories:
            category_item = self.add_category_item(lms_item, category)
            
        # Add courses (not in categories)
        for course in self.lms.courses:
            if not course.category:
                course_item = self.add_course_item(lms_item, course)
                
        # Add enrolled courses
        if self.lms.enrolled_courses:
            enrolled_item = QTreeWidgetItem(lms_item)
            enrolled_item.setText(0, "Enrolled Courses")
            enrolled_item.setText(2, "Group")
            
            for course in self.lms.enrolled_courses:
                course_item = self.add_course_item(enrolled_item, course)
        
        # Expand the root item
        lms_item.setExpanded(True)
        
    def add_category_item(self, parent: QTreeWidgetItem, category: ICategory) -> QTreeWidgetItem:
        """Add a category item to the tree"""
        category_item = QTreeWidgetItem(parent)
        category_item.setText(0, category.name or f"Category {category.id}")
        category_item.setText(1, str(category.id))
        category_item.setText(2, "Category")
        category_item.setData(0, Qt.UserRole, category)
        
        # Add courses in this category
        for course in category.courses:
            self.add_course_item(category_item, course)
            
        return category_item
        
    def add_course_item(self, parent: QTreeWidgetItem, course: ICourse) -> QTreeWidgetItem:
        """Add a course item to the tree"""
        course_item = QTreeWidgetItem(parent)
        course_item.setText(0, course.name or f"Course {course.id}")
        course_item.setText(1, str(course.id))
        course_item.setText(2, "Course")
        course_item.setData(0, Qt.UserRole, course)
        
        # Add enrolled users
        if course.enrolled_users:
            users_item = QTreeWidgetItem(course_item)
            users_item.setText(0, "Users")
            users_item.setText(2, "Group")
            
            for user in course.enrolled_users:
                self.add_user_item(users_item, user)
                
        # Add user groups
        if course.user_groups:
            groups_item = QTreeWidgetItem(course_item)
            groups_item.setText(0, "Groups")
            groups_item.setText(2, "Group")
            
            for group in course.user_groups:
                self.add_group_item(groups_item, group)
                
        # Add course content
        if course.course_content:
            content_item = QTreeWidgetItem(course_item)
            content_item.setText(0, "Content")
            content_item.setText(2, "Group")
            
            for section in course.course_content:
                self.add_section_item(content_item, section)
                
        return course_item
        
    def add_user_item(self, parent: QTreeWidgetItem, user: IUser) -> QTreeWidgetItem:
        """Add a user item to the tree"""
        user_item = QTreeWidgetItem(parent)
        user_item.setText(0, user.full_name or f"User {user.id}")
        user_item.setText(1, str(user.id))
        user_item.setText(2, "User")
        user_item.setData(0, Qt.UserRole, user)
        
        # Add email as additional info
        if user.email:
            user_item.setText(3, user.email)
            
        return user_item
        
    def add_group_item(self, parent: QTreeWidgetItem, group) -> QTreeWidgetItem:
        """Add a user group item to the tree"""
        group_item = QTreeWidgetItem(parent)
        group_item.setText(0, group.group_name or f"Group {group.id}")
        group_item.setText(1, str(group.id))
        group_item.setText(2, "Group")
        group_item.setData(0, Qt.UserRole, group)
        
        # Add users in the group
        for user in group.users_in_group:
            self.add_user_item(group_item, user)
            
        return group_item
        
    def add_section_item(self, parent: QTreeWidgetItem, section) -> QTreeWidgetItem:
        """Add a section item to the tree"""
        section_item = QTreeWidgetItem(parent)
        section_item.setText(0, section.name or f"Section {section.id}")
        section_item.setText(1, str(section.id))
        section_item.setText(2, "Section")
        section_item.setData(0, Qt.UserRole, section)
        
        # Add modules in the section
        for module in section.modules:
            self.add_module_item(section_item, module)
            
        return section_item
        
    def add_module_item(self, parent: QTreeWidgetItem, module) -> QTreeWidgetItem:
        """Add a module item to the tree"""
        module_item = QTreeWidgetItem(parent)
        module_item.setText(0, module.name or f"Module {module.id}")
        module_item.setText(1, str(module.id))
        module_item.setText(2, "Module")
        module_item.setData(0, Qt.UserRole, module)
        
        # Add module type
        if module.mod_name:
            module_item.setText(3, module.mod_name)
            
        return module_item
        
    def filter_items(self, filter_text: str):
        """Filter tree items based on the filter text"""
        if not filter_text:
            # Show all items
            self.show_all_items()
            return
            
        filter_text = filter_text.lower()
        
        # Hide all items first
        self.hide_all_items()
        
        # Show items that match the filter
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
        has_visible_child = False
        
        for i in range(item.childCount()):
            child = item.child(i)
            if self._filter_recursive(child, filter_text):
                has_visible_child = True
                
        # Check if current item matches filter
        matches_filter = False
        data = item.data(0, Qt.UserRole)
        if data:
            if hasattr(data, 'filter_content'):
                matches_filter = filter_text in data.filter_content.lower()
            elif hasattr(data, 'name'):
                matches_filter = filter_text in str(data.name).lower()
            elif hasattr(data, 'full_name'):
                matches_filter = filter_text in str(data.full_name).lower()
                
        # Show item if it matches or has visible children
        if matches_filter or has_visible_child:
            item.setHidden(False)
            return True
        else:
            item.setHidden(True)
            return False
            
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        data = item.data(0, Qt.UserRole)
        if data:
            self.item_selected.emit(data)
            
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click"""
        data = item.data(0, Qt.UserRole)
        if data:
            if hasattr(data, 'course_content'):  # It's a course
                self.course_double_clicked.emit(data)
            elif hasattr(data, 'full_name'):  # It's a user
                self.user_double_clicked.emit(data)
                
    def show_context_menu(self, position):
        """Show context menu for the selected item"""
        item = self.itemAt(position)
        if not item:
            return
            
        data = item.data(0, Qt.UserRole)
        if not data:
            return
            
        menu = QMenu(self)
        
        # Add context menu actions based on item type
        if hasattr(data, 'course_content'):  # Course
            refresh_action = menu.addAction("Refresh Course")
            view_content_action = menu.addAction("View Content")
            view_users_action = menu.addAction("View Users")
            
        elif hasattr(data, 'full_name'):  # User
            view_profile_action = menu.addAction("View Profile")
            view_grades_action = menu.addAction("View Grades")
            
        elif hasattr(data, 'courses'):  # Category
            refresh_action = menu.addAction("Refresh Category")
            
        # Show the menu
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
        # Handle menu actions
        if action:
            self.handle_context_menu_action(action, data, item)
            
    def handle_context_menu_action(self, action, data, item):
        """Handle context menu action"""
        action_text = action.text()
        
        if action_text == "Refresh Course":
            self.refresh_course(data)
        elif action_text == "View Content":
            self.view_course_content(data)
        elif action_text == "View Users":
            self.view_course_users(data)
        elif action_text == "View Profile":
            self.view_user_profile(data)
        elif action_text == "View Grades":
            self.view_user_grades(data)
        elif action_text == "Refresh Category":
            self.refresh_category(data)
            
    def refresh_course(self, course):
        """Refresh course data"""
        # This would trigger a refresh of course data from the LMS
        print(f"Refreshing course: {course.name}")
        
    def view_course_content(self, course):
        """View course content"""
        print(f"Viewing content for course: {course.name}")
        
    def view_course_users(self, course):
        """View course users"""
        print(f"Viewing users for course: {course.name}")
        
    def view_user_profile(self, user):
        """View user profile"""
        print(f"Viewing profile for user: {user.full_name}")
        
    def view_user_grades(self, user):
        """View user grades"""
        print(f"Viewing grades for user: {user.full_name}")
        
    def refresh_category(self, category):
        """Refresh category data"""
        print(f"Refreshing category: {category.name}")
        
    def refresh_data(self):
        """Refresh all data in the tree"""
        if self.lms:
            self.populate_tree()
