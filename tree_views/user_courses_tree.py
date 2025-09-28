"""
User Courses Tree View for LMS Explorer
Displays courses that a user is enrolled in
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from tree_views.custom_tree import CustomTreeWidget, TreeData, NodeTypes
from data_models import IUser, ICourse
from helpers.form_factory import FormFactory


class UserCoursesTreeWidget(CustomTreeWidget):
    """
    Tree widget for displaying courses that a user is enrolled in
    """
    
    # Signal emitted when a course is double-clicked
    course_double_clicked = pyqtSignal(object, object)  # course, user
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._courses = []
        self._user = None
        
        self._setup_tree()
        
    def _setup_tree(self):
        """Setup the tree widget properties"""
        # Set tree options
        self.setHeaderHidden(False)
        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        
        # Setup columns
        self.setColumnCount(2)
        self.setHeaderLabels(["Course", "Full Name"])
        
        # Configure header
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setStretchLastSection(False)
        
        # Enable full row selection
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setSelectionBehavior(QTreeWidget.SelectRows)
        
        # Connect signals
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        
    def set_user(self, user: IUser):
        """
        Set the user and display their enrolled courses
        
        Args:
            user: The user object
        """
        self._user = user
        
        if user:
            self._courses = user.get_other_enrolled_courses()
        else:
            self._courses = []
            
        self._refresh_tree()
        
    def get_selected_course(self) -> ICourse:
        """
        Get the currently selected course
        
        Returns:
            The selected course object or None
        """
        selected_items = self.selectedItems()
        if selected_items:
            item = selected_items[0]
            data = item.data(0, Qt.UserRole)
            if data and data.node_type == NodeTypes.COURSE:
                return data.course
        return None
        
    def filter_by_text(self, text: str):
        """
        Filter courses by text
        
        Args:
            text: The filter text
        """
        if not text:
            # Show all items if no filter text
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                item.setHidden(False)
            return
            
        filter_text = text.lower()
        
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.UserRole)
            
            if data and data.node_type == NodeTypes.COURSE:
                course = data.course
                # Check if filter text matches course name or short name
                course_text = f"{course.get_name()} {course.get_short_name()} {course.get_full_name()}".lower()
                
                if filter_text in course_text:
                    item.setHidden(False)
                else:
                    item.setHidden(True)
                    
    def _refresh_tree(self):
        """Refresh the tree with current courses"""
        self.clear()
        
        if not self._user or not self._courses:
            return
            
        # Add courses as top-level items
        for course in self._courses:
            course_item = self._create_course_item(course)
            self.addTopLevelItem(course_item)
            
        # Resize columns to content
        self.resizeColumnToContents(0)
        
    def _create_course_item(self, course: ICourse) -> QTreeWidgetItem:
        """
        Create a tree item for a course
        
        Args:
            course: The course object
            
        Returns:
            The created tree item
        """
        item = QTreeWidgetItem()
        
        # Create tree data
        tree_data = TreeData()
        tree_data.node_type = NodeTypes.COURSE
        tree_data.course = course
        
        # Set item data
        item.setData(0, Qt.UserRole, tree_data)
        
        # Set text
        item.setText(0, course.get_short_name() or course.get_name())
        item.setText(1, course.get_full_name() or course.get_name())
        
        # Set font
        font = QFont()
        font.setBold(False)
        item.setFont(0, font)
        item.setFont(1, font)
        
        return item
        
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Handle item double-click event
        
        Args:
            item: The double-clicked item
            column: The column that was clicked
        """
        data = item.data(0, Qt.UserRole)
        if data and data.node_type == NodeTypes.COURSE:
            course = data.course
            if self._user:
                # Emit signal with course and user
                self.course_double_clicked.emit(course, self._user)
                # Open course form using form factory
                FormFactory.view_form(course, self._user)
