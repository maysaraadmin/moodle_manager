"""
User Grades Dialog for LMS Explorer
Dialog to display user grades and grade information
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, 
                             QTextEdit, QMessageBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from lms_interface import IUser, ICourse, IGradeItem


class UserGradesDialog(QDialog):
    """Dialog to display user grades"""
    
    def __init__(self, user: IUser, parent=None):
        super().__init__(parent)
        
        self.user = user
        self.setWindowTitle(f"User Grades - {user.full_name or f'{user.first_name} {user.last_name}'}")
        self.setModal(True)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.setup_ui()
        self.load_grades()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(f"User: {self.full_name or f'{self.user.first_name} {self.user.last_name}'}")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Course info
        course = self.user.get_course()
        if course:
            course_label = QLabel(f"Course: {course.fullname or course.shortname}")
            course_label.setStyleSheet("font-size: 14px; margin: 5px;")
            layout.addWidget(course_label)
        
        # Grades table
        self.grades_table = QTableWidget()
        self.grades_table.setColumnCount(4)
        self.grades_table.setHorizontalHeaderLabels(["Grade Item", "Grade", "Maximum Grade", "Percentage"])
        self.grades_table.itemSelectionChanged.connect(self.on_grade_selected)
        layout.addWidget(self.grades_table)
        
        # Details section
        details_layout = QVBoxLayout()
        
        # Details label
        self.details_label = QLabel("Grade Details")
        self.details_label.setStyleSheet("font-weight: bold; margin: 5px;")
        details_layout.addWidget(self.details_label)
        
        # Details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        
        layout.addLayout(details_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_grades)
        button_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def load_grades(self):
        """Load user grades"""
        self.grades_table.setRowCount(0)
        self.details_text.clear()
        
        try:
            course = self.user.get_course()
            if not course:
                self.details_text.setText("User is not associated with any course.")
                return
            
            # Get grade items for the course
            grade_items = course.get_grade_items()
            
            if not grade_items:
                self.details_text.setText("No grade items found for this course.")
                return
            
            # Populate the grades table
            self.grades_table.setRowCount(len(grade_items))
            
            for row, grade_item in enumerate(grade_items):
                # Grade item name
                name_item = QTableWidgetItem(grade_item.get_item_name() or f"Grade Item {row + 1}")
                name_item.setData(Qt.UserRole, grade_item)
                self.grades_table.setItem(row, 0, name_item)
                
                # Grade (placeholder - would need to get actual user grade from API)
                grade_item_widget = QTableWidgetItem("N/A")
                self.grades_table.setItem(row, 1, grade_item_widget)
                
                # Maximum grade (placeholder)
                max_grade_item = QTableWidgetItem("100")
                self.grades_table.setItem(row, 2, max_grade_item)
                
                # Percentage (placeholder)
                percentage_item = QTableWidgetItem("N/A")
                self.grades_table.setItem(row, 3, percentage_item)
            
            # Resize columns
            self.grades_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
            self.grades_table.horizontalHeader().setStretchLastSection(True)
            
            self.details_text.setText(f"Loaded {len(grade_items)} grade items for this course.")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load user grades: {str(e)}")
            
    def on_grade_selected(self):
        """Handle grade item selection"""
        selected_items = self.grades_table.selectedItems()
        if not selected_items:
            return
        
        # Get the row of the first selected item
        row = selected_items[0].row()
        grade_item = self.grades_table.item(row, 0).data(Qt.UserRole)
        
        if grade_item:
            self.show_grade_details(grade_item)
            
    def show_grade_details(self, grade_item: IGradeItem):
        """Show grade item details"""
        self.details_label.setText(f"Grade Item: {grade_item.get_item_name()}")
        
        details = f"Grade Item Name: {grade_item.get_item_name() or 'N/A'}\n"
        details += f"Item Type: Grade Item\n"
        
        # Add course information
        course = self.user.get_course()
        if course:
            details += f"Course: {course.fullname or course.shortname}\n"
        
        # Add user information
        details += f"User: {self.user.full_name or f'{self.user.first_name} {self.user.last_name}'}\n"
        details += f"User ID: {self.user.id}\n"
        
        # Note: In a real implementation, you would fetch the actual grade data
        # from the Moodle API for this specific user and grade item
        details += "\nNote: Actual grade values would be fetched from the Moodle API."
        
        self.details_text.setText(details)
