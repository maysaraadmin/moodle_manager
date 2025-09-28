"""
Network Tree Widget
Tree view for displaying LMS network structure with enhanced icons and styling
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap, QColor

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
        """Setup the tree widget UI with enhanced styling"""
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

        # Enhanced styling
        self.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                alternate-background-color: #f9f9f9;
                selection-background-color: #0078d4;
                outline: none;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                height: 30px;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #f0f8ff;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #ddd;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        # Set column widths
        self.setColumnWidth(0, 300)  # Name column
        self.setColumnWidth(1, 100)  # ID column
        self.setColumnWidth(2, 100)  # Type column

    def set_lms(self, lms: ILMS):
        """Set the LMS instance and populate the tree"""
        self.lms = lms
        self.populate_tree()

    def populate_tree(self):
        """Populate the tree with LMS data and icons"""
        self.clear()

        if not self.lms:
            return

        # Add LMS root item with icon
        lms_item = QTreeWidgetItem(self)
        lms_item.setText(0, self.lms.name or "Learning Management System")
        lms_item.setText(1, str(self.lms.host or ""))
        lms_item.setText(2, "LMS")
        lms_item.setData(0, Qt.UserRole, self.lms)
        lms_item.setIcon(0, self.get_icon("lms"))

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
            enrolled_item.setIcon(0, self.get_icon("group"))
            enrolled_item.setData(0, Qt.UserRole, {"type": "enrolled_group"})

            for course in self.lms.enrolled_courses:
                course_item = self.add_course_item(enrolled_item, course)

        # Expand the root item
        lms_item.setExpanded(True)

    def add_category_item(self, parent: QTreeWidgetItem, category: ICategory) -> QTreeWidgetItem:
        """Add a category item to the tree with icon"""
        category_item = QTreeWidgetItem(parent)
        category_item.setText(0, category.name or f"Category {category.id}")
        category_item.setText(1, str(category.id))
        category_item.setText(2, "Category")
        category_item.setData(0, Qt.UserRole, category)
        category_item.setIcon(0, self.get_icon("category"))

        # Add courses in this category
        for course in category.courses:
            self.add_course_item(category_item, course)

        return category_item

    def add_course_item(self, parent: QTreeWidgetItem, course: ICourse) -> QTreeWidgetItem:
        """Add a course item to the tree with icon"""
        course_item = QTreeWidgetItem(parent)
        course_item.setText(0, course.name or f"Course {course.id}")
        course_item.setText(1, str(course.id))
        course_item.setText(2, "Course")
        course_item.setData(0, Qt.UserRole, course)
        course_item.setIcon(0, self.get_icon("course"))

        # Add enrolled users count if available
        if course.enrolled_users:
            users_item = QTreeWidgetItem(course_item)
            users_item.setText(0, f"👥 Users ({len(course.enrolled_users)})")
            users_item.setText(2, "Group")
            users_item.setIcon(0, self.get_icon("users"))

            for user in course.enrolled_users:
                self.add_user_item(users_item, user)

        # Add user groups count if available
        if course.user_groups:
            groups_item = QTreeWidgetItem(course_item)
            groups_item.setText(0, f"👨‍👩‍👧‍👦 Groups ({len(course.user_groups)})")
            groups_item.setText(2, "Group")
            groups_item.setIcon(0, self.get_icon("group"))

            for group in course.user_groups:
                self.add_group_item(groups_item, group)

        # Add course content count if available
        if course.course_content:
            content_item = QTreeWidgetItem(course_item)
            content_item.setText(0, f"📚 Content ({len(course.course_content)} sections)")
            content_item.setText(2, "Group")
            content_item.setIcon(0, self.get_icon("content"))

            for section in course.course_content:
                self.add_section_item(content_item, section)

        return course_item

    def add_user_item(self, parent: QTreeWidgetItem, user: IUser) -> QTreeWidgetItem:
        """Add a user item to the tree with icon"""
        user_item = QTreeWidgetItem(parent)
        user_item.setText(0, user.full_name or f"User {user.id}")
        user_item.setText(1, str(user.id))
        user_item.setText(2, "User")
        user_item.setData(0, Qt.UserRole, user)
        user_item.setIcon(0, self.get_icon("user"))

        # Add email as additional info
        if user.email:
            user_item.setText(3, user.email)

        return user_item

    def add_group_item(self, parent: QTreeWidgetItem, group) -> QTreeWidgetItem:
        """Add a user group item to the tree with icon"""
        group_item = QTreeWidgetItem(parent)
        group_item.setText(0, group.group_name or f"Group {group.id}")
        group_item.setText(1, str(group.id))
        group_item.setText(2, "Group")
        group_item.setData(0, Qt.UserRole, group)
        group_item.setIcon(0, self.get_icon("group"))

        # Add users in the group
        for user in group.users_in_group:
            self.add_user_item(group_item, user)

        return group_item

    def add_section_item(self, parent: QTreeWidgetItem, section) -> QTreeWidgetItem:
        """Add a section item to the tree with icon"""
        section_item = QTreeWidgetItem(parent)
        section_item.setText(0, section.name or f"Section {section.id}")
        section_item.setText(1, str(section.id))
        section_item.setText(2, "Section")
        section_item.setData(0, Qt.UserRole, section)
        section_item.setIcon(0, self.get_icon("section"))

        # Add modules in the section
        for module in section.modules:
            self.add_module_item(section_item, module)

        return section_item

    def add_module_item(self, parent: QTreeWidgetItem, module) -> QTreeWidgetItem:
        """Add a module item to the tree with icon"""
        module_item = QTreeWidgetItem(parent)
        module_item.setText(0, module.name or f"Module {module.id}")
        module_item.setText(1, str(module.id))
        module_item.setText(2, "Module")
        module_item.setData(0, Qt.UserRole, module)

        # Set icon based on module type
        module_item.setIcon(0, self.get_icon(f"module_{module.mod_name}"))

        # Add module type
        if module.mod_name:
            module_item.setText(3, module.mod_name)

        return module_item

    def get_icon(self, icon_type):
        """Get icon for different item types"""
        # Create simple colored icons
        size = 16

        if icon_type == "lms":
            return self.create_colored_icon(QColor(0, 120, 215), size)  # Blue
        elif icon_type == "category":
            return self.create_colored_icon(QColor(255, 193, 7), size)  # Yellow
        elif icon_type == "course":
            return self.create_colored_icon(QColor(76, 175, 80), size)  # Green
        elif icon_type == "user":
            return self.create_colored_icon(QColor(156, 39, 176), size)  # Purple
        elif icon_type == "group":
            return self.create_colored_icon(QColor(255, 87, 34), size)  # Orange
        elif icon_type == "content":
            return self.create_colored_icon(QColor(33, 150, 243), size)  # Light Blue
        elif icon_type == "section":
            return self.create_colored_icon(QColor(0, 188, 212), size)  # Cyan
        elif icon_type.startswith("module_"):
            # Different colors for different module types
            module_colors = {
                "forum": QColor(139, 69, 19),  # Brown
                "quiz": QColor(205, 220, 57),  # Lime
                "assignment": QColor(255, 64, 129),  # Pink
                "resource": QColor(103, 58, 183),  # Deep Purple
                "page": QColor(0, 151, 167),  # Teal
            }
            color = module_colors.get(icon_type.replace("module_", ""), QColor(158, 158, 158))
            return self.create_colored_icon(color, size)
        elif icon_type == "users":
            return self.create_colored_icon(QColor(63, 81, 181), size)  # Indigo
        else:
            return self.create_colored_icon(QColor(117, 117, 117), size)  # Default Gray

    def create_colored_icon(self, color, size):
        """Create a simple colored square icon"""
        pixmap = QPixmap(size, size)
        pixmap.fill(color)
        return QIcon(pixmap)

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

    def filter_items(self, filter_text):
        """Filter tree items based on text"""
        if not filter_text:
            # Show all items if no filter
            self.show_all_items()
            return

        filter_text = filter_text.lower()
        root = self.invisibleRootItem()

        for i in range(root.childCount()):
            item = root.child(i)
            self.filter_item_recursive(item, filter_text)

    def filter_item_recursive(self, item, filter_text):
        """Recursively filter tree items"""
        if not item:
            return

        # Check if this item matches the filter
        item_matches = False
        data = item.data(0, Qt.UserRole)

        if data:
            # Check filter content if available
            if hasattr(data, 'filter_content'):
                item_matches = filter_text in data.filter_content.lower()
            else:
                # Fallback to text content
                item_text = item.text(0).lower()
                item_matches = filter_text in item_text

        # Show/hide based on match
        item.setHidden(not item_matches)

        # Check children
        for i in range(item.childCount()):
            child = item.child(i)
            child_matches = self.filter_item_recursive(child, filter_text)

            # If any child matches, show this item too
            if child_matches:
                item_matches = True
                item.setHidden(False)

        return item_matches

    def show_all_items(self):
        """Show all tree items"""
        def show_recursive(item):
            if not item:
                return
            item.setHidden(False)
            for i in range(item.childCount()):
                show_recursive(item.child(i))

        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            show_recursive(root.child(i))

    def on_item_clicked(self, item, column):
        """Handle item click"""
        data = item.data(0, Qt.UserRole)
        if data:
            self.item_selected.emit(data)

    def on_item_double_clicked(self, item, column):
        """Handle item double click"""
        data = item.data(0, Qt.UserRole)
        if data:
            if hasattr(data, 'course_content'):  # It's a course
                self.course_double_clicked.emit(data)
            elif hasattr(data, 'full_name'):  # It's a user
                self.user_double_clicked.emit(data)
