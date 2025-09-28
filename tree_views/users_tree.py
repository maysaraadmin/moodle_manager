"""
Users Tree Widget
Tree view for displaying LMS users
"""

from typing import Optional, List
from PyQt5.QtWidgets import QTreeWidgetItem, QMenu, QAction, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from lms_interface import IUser
from tree_views.custom_tree import CustomTreeWidget, TreeData, NodeTypes
from helpers.browser import BrowserHelper


class UsersTreeWidget(CustomTreeWidget):
    """Tree widget for displaying LMS users"""
    
    # Signals
    user_selected = pyqtSignal(object)  # Emitted when a user is selected
    user_double_clicked = pyqtSignal(object)  # Emitted when a user is double-clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.users: List[IUser] = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the tree widget UI"""
        # Set header labels
        self.setHeaderLabels(["Full Name", "First Name", "Last Name", "Email"])
        
        # Set column properties
        header = self.header()
        header.setStretchLastSection(False)
        for i in range(4):
            header.setSectionResizeMode(i, header.Stretch)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.item_double_clicked.connect(self.on_item_double_clicked)
        
    def set_users(self, users: List[IUser]):
        """Set the users list and populate the tree"""
        self.users = users
        self.populate_tree()
        
    def populate_tree(self):
        """Populate the tree with users data"""
        self.clear()
        
        for user in self.users:
            self.add_user_item(user)
            
        # Auto-resize columns
        self.header().resizeSections(QHeaderView.ResizeToContents)
        
    def add_user_item(self, user: IUser) -> QTreeWidgetItem:
        """Add a user item to the tree"""
        data = TreeData()
        data.node_type = NodeTypes.USER
        data.user = user
        
        item = QTreeWidgetItem(self)
        item.setText(0, user.full_name or f"User {user.id}")
        item.setText(1, user.first_name or "")
        item.setText(2, user.last_name or "")
        item.setText(3, user.email or "")
        
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
        """Filter users by text"""
        if not filter_text:
            self.show_all_items()
            return
            
        filter_text = filter_text.lower()
        
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = self.get_item_data(item)
            
            if data and data.node_type == NodeTypes.USER and data.user:
                compare_text = data.user.filter_content.lower()
                item.setHidden(filter_text not in compare_text)
            else:
                item.setHidden(True)
                
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
        # This would typically open a dialog or form
        # For now, we'll just emit a signal
        self.user_double_clicked.emit(user)
        
    def view_user_grades(self, user: IUser):
        """View user grades"""
        try:
            from dialogs.user_grades_dialog import UserGradesDialog
            dialog = UserGradesDialog(user, self)
            dialog.exec_()
        except ImportError:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "User Grades", f"Viewing grades for user: {user.full_name or f'{user.first_name} {user.last_name}'}")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to open user grades: {str(e)}")
        
    def open_user_in_browser(self, user: IUser):
        """Open user profile in browser"""
        if user and user.course:
            BrowserHelper.open_user_profile(user.course, user)
            
    def refresh(self):
        """Refresh the tree"""
        self.populate_tree()
        
    def clear_users(self):
        """Clear all users from the tree"""
        self.clear()
        self.users.clear()
