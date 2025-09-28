"""
Courses Tree Widget
Tree view for displaying LMS courses
"""

from typing import Optional, List
from PyQt5.QtWidgets import QTreeWidgetItem, QMenu, QAction, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import ILMS, ICourse
from tree_views.custom_tree import CustomTreeWidget, TreeData, NodeTypes
from helpers.utils import Utils
from helpers.browser import BrowserHelper


class CoursesTreeWidget(CustomTreeWidget):
    """Tree widget for displaying LMS courses"""
    
    # Signals
    course_selected = pyqtSignal(object)  # Emitted when a course is selected
    course_double_clicked = pyqtSignal(object)  # Emitted when a course is double-clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.lms: Optional[ILMS] = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the tree widget UI"""
        # Set header labels
        self.setHeaderLabels(["Short Name", "Full Name", "Start Date", "End Date", "Time Created", "Time Modified"])
        
        # Set column properties
        header = self.header()
        header.setStretchLastSection(False)
        for i in range(6):
            header.setSectionResizeMode(i, header.Stretch)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.item_double_clicked.connect(self.on_item_double_clicked)
        
    def set_lms(self, lms: ILMS):
        """Set the LMS instance and populate the tree"""
        self.lms = lms
        self.populate_tree()
        
    def populate_tree(self):
        """Populate the tree with courses data"""
        self.clear()
        
        if not self.lms:
            return
            
        for course in self.lms.flat_courses:
            self.add_course_item(course)
            
        # Auto-resize columns
        self.header().resizeSections(QHeaderView.ResizeToContents)
        
    def add_course_item(self, course: ICourse) -> QTreeWidgetItem:
        """Add a course item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.COURSE
        data.course = course
        
        item = QTreeWidgetItem(self)
        item.setText(0, course.shortname or f"Course {course.id}")
        item.setText(1, course.fullname or "")
        item.setText(2, Utils.format_datetime_blank(course.start_date))
        item.setText(3, Utils.format_datetime_blank(course.end_date))
        item.setText(4, Utils.format_datetime_blank(course.time_created))
        item.setText(5, Utils.format_datetime_blank(course.time_modified))
        
        # Store the data object
        item.setData(0, Qt.UserRole, data)
        
        # Set appropriate icon based on group mode
        self.set_course_icon(item, course)
        
        return item
        
    def set_course_icon(self, item: QTreeWidgetItem, course: ICourse):
        """Set the appropriate icon for a course based on its group mode"""
        if course.groupmode == 1:  # Separate groups
            icon = self.image_helper.get_icon('res_groups_separate_groups')
        elif course.groupmode == 2:  # Visible groups
            icon = self.image_helper.get_icon('res_groups_visible_groups')
        else:  # No groups
            icon = self.image_helper.get_icon('res_groups_no_groups')
            
        if icon:
            item.setIcon(0, icon)
            
    def get_selected_course(self) -> Optional[ICourse]:
        """Get the selected course"""
        data = self.get_selected_item_data()
        if data and data.node_type == NodeTypes.COURSE:
            return data.course
        return None
        
    def filter_by_text(self, filter_text: str):
        """Filter courses by text"""
        if not filter_text:
            self.show_all_items()
            return
            
        filter_text = filter_text.lower()
        
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = self.get_item_data(item)
            
            if data and data.node_type == NodeTypes.COURSE and data.course:
                compare_text = data.course.filter_content.lower()
                item.setHidden(filter_text not in compare_text)
            else:
                item.setHidden(True)
                
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        data = self.get_item_data(item)
        if data and data.node_type == NodeTypes.COURSE:
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
            if data and data.node_type == NodeTypes.COURSE:
                menu = QMenu(self)
                
                # Add context menu actions
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
                
    def view_course_content(self, course: ICourse):
        """View course content"""
        try:
            from dialogs.course_content_dialog import CourseContentDialog
            dialog = CourseContentDialog(course, self)
            dialog.exec_()
        except ImportError:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Course Content", f"Viewing content for course: {course.fullname or course.shortname}")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to open course content: {str(e)}")
        
    def view_course_users(self, course: ICourse):
        """View course users"""
        try:
            from dialogs.course_users_dialog import CourseUsersDialog
            dialog = CourseUsersDialog(course, self)
            dialog.exec_()
        except ImportError:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Course Users", f"Viewing users for course: {course.fullname or course.shortname}")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to open course users: {str(e)}")
        
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
        
    def clear_courses(self):
        """Clear all courses from the tree"""
        self.clear()
        self.lms = None
