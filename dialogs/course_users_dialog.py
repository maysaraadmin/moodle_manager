"""
Course Users Dialog for LMS Explorer
Dialog to display course users and their information
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, 
                             QSplitter, QTextEdit, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from lms_interface import ICourse, IUser


class CourseUsersDialog(QDialog):
    """Dialog to display course users"""
    
    def __init__(self, course: ICourse, parent=None):
        super().__init__(parent)
        
        self.course = course
        self.setWindowTitle(f"Course Users - {course.fullname or course.shortname}")
        self.setModal(True)
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        
        self.setup_ui()
        self.load_users()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(f"Course: {self.course.fullname or self.course.shortname}")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by Role:"))
        self.role_filter = QComboBox()
        self.role_filter.addItem("All Users")
        self.role_filter.currentTextChanged.connect(self.on_role_filter_changed)
        filter_layout.addWidget(self.role_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Users tree
        self.users_tree = QTreeWidget()
        self.users_tree.setHeaderLabels(["Name", "Username", "Email", "Roles"])
        self.users_tree.itemClicked.connect(self.on_item_clicked)
        splitter.addWidget(self.users_tree)
        
        # Right side - Details
        right_widget = QVBoxLayout()
        
        # Details label
        self.details_label = QLabel("Select a user to view details")
        self.details_label.setStyleSheet("font-weight: bold; margin: 5px;")
        right_widget.addWidget(self.details_label)
        
        # Details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_widget.addWidget(self.details_text)
        
        # Add right widget to splitter
        right_container = QWidget()
        right_container.setLayout(right_widget)
        splitter.addWidget(right_container)
        
        # Set splitter sizes
        splitter.setSizes([500, 400])
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_users)
        button_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def load_users(self):
        """Load course users"""
        self.users_tree.clear()
        self.details_text.clear()
        self.details_label.setText("Select a user to view details")
        
        try:
            # Get enrolled users
            users = self.course.get_enrolled_users()
            
            if not users:
                self.details_label.setText("No users found")
                self.details_text.setText("This course has no enrolled users.")
                return
            
            # Get available roles for filtering
            roles = set()
            for user in users:
                if hasattr(user, 'get_roles'):
                    user_roles = user.get_roles()
                    if user_roles:
                        roles.update(user_roles)
            
            # Update role filter combo box
            current_role = self.role_filter.currentText()
            self.role_filter.clear()
            self.role_filter.addItem("All Users")
            for role in sorted(roles):
                self.role_filter.addItem(role)
            
            # Restore previous selection if possible
            index = self.role_filter.findText(current_role)
            if index >= 0:
                self.role_filter.setCurrentIndex(index)
            
            # Add users to tree
            for user in users:
                user_item = QTreeWidgetItem(self.users_tree)
                user_item.setText(0, user.fullname or f"{user.first_name} {user.last_name}")
                user_item.setText(1, user.username or "")
                user_item.setText(2, user.email or "")
                
                # Get user roles
                user_roles = []
                if hasattr(user, 'get_roles'):
                    user_roles = user.get_roles()
                user_item.setText(3, ", ".join(user_roles) if user_roles else "Student")
                
                # Store user data
                user_item.setData(0, Qt.UserRole, user)
            
            # Resize columns
            self.users_tree.header().resizeSections(QTreeWidget.ResizeToContents)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load course users: {str(e)}")
            
    def on_role_filter_changed(self, role_text: str):
        """Handle role filter change"""
        for i in range(self.users_tree.topLevelItemCount()):
            item = self.users_tree.topLevelItem(i)
            user = item.data(0, Qt.UserRole)
            
            if user and role_text != "All Users":
                user_roles = []
                if hasattr(user, 'get_roles'):
                    user_roles = user.get_roles()
                item.setHidden(role_text not in user_roles)
            else:
                item.setHidden(False)
                
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click in the users tree"""
        user = item.data(0, Qt.UserRole)
        
        if user:
            self.show_user_details(user)
            
    def show_user_details(self, user: IUser):
        """Show user details"""
        self.details_label.setText(f"User: {user.fullname or f'{user.first_name} {user.last_name}'}")
        
        details = f"User ID: {user.id}\n"
        details += f"First Name: {user.first_name or 'N/A'}\n"
        details += f"Last Name: {user.last_name or 'N/A'}\n"
        details += f"Full Name: {user.fullname or 'N/A'}\n"
        details += f"Username: {user.username or 'N/A'}\n"
        details += f"Email: {user.email or 'N/A'}\n"
        
        # Get user roles
        user_roles = []
        if hasattr(user, 'get_roles'):
            user_roles = user.get_roles()
        details += f"Roles: {', '.join(user_roles) if user_roles else 'Student'}\n"
        
        # Get course info
        course = user.get_course()
        if course:
            details += f"Course: {course.fullname or course.shortname}\n"
        
        # Get LMS info
        lms = user.get_lms()
        if lms:
            details += f"LMS: {lms.get_name() or 'N/A'}\n"
        
        self.details_text.setText(details)
