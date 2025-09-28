"""
Reports helper for LMS Explorer
Handles report generation and export functionality
"""

import os
from datetime import datetime
from typing import List, Optional
from lms_interface import ILMS, ICourse, IUser, IUsersGroup
from helpers.excel import ExcelHelper
from helpers.utils import Utils


class ReportsHelper:
    """Helper class for generating reports"""
    
    def __init__(self):
        self.excel_helper = ExcelHelper()
    
    def export_course_to_excel(self, course: ICourse, filename: str = None):
        """
        Export course data to Excel
        Args:
            course: The course to export
            filename: Optional filename, if None generates automatic filename
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = Utils.safe_filename(getattr(course, 'name', f'Course_{course.id}'))
            filename = f"Course_{safe_name}_{timestamp}.xlsx"
        
        self.excel_helper.create_workbook()
        
        # Course header
        course_name = getattr(course, 'name', '')
        course_id = getattr(course, 'id', '')
        
        self.excel_helper.worksheet.cell(row=1, column=1, value=f"Course: {course_name}")
        self.excel_helper.worksheet.cell(row=1, column=3, value=f"ID: {course_id}")
        
        current_row = 5
        
        # Export user groups if available
        user_groups = getattr(course, 'user_groups', [])
        if user_groups:
            for group in user_groups:
                group_name = getattr(group, 'group_name', '')
                self.excel_helper.worksheet.cell(row=current_row, column=2, value=group_name)
                current_row += 1
                
                # Export users in group
                users_in_group = getattr(group, 'users_in_group', [])
                for user in users_in_group:
                    first_name = getattr(user, 'first_name', '')
                    last_name = getattr(user, 'last_name', '')
                    email = getattr(user, 'email', '')
                    
                    self.excel_helper.worksheet.cell(row=current_row, column=3, value=first_name)
                    self.excel_helper.worksheet.cell(row=current_row, column=4, value=last_name)
                    self.excel_helper.worksheet.cell(row=current_row, column=5, value=email)
                    current_row += 1
                
                current_row += 1  # Space between groups
        else:
            # Export enrolled users if no groups
            enrolled_users = getattr(course, 'enrolled_users', [])
            for user in enrolled_users:
                first_name = getattr(user, 'first_name', '')
                last_name = getattr(user, 'last_name', '')
                email = getattr(user, 'email', '')
                
                self.excel_helper.worksheet.cell(row=current_row, column=2, value=first_name)
                self.excel_helper.worksheet.cell(row=current_row, column=3, value=last_name)
                self.excel_helper.worksheet.cell(row=current_row, column=4, value=email)
                current_row += 1
        
        self.excel_helper.auto_fit_columns()
        self.excel_helper.save_workbook(filename)
    
    def export_courses_to_excel(self, lms: ILMS, filename: str = None):
        """
        Export all courses from LMS to Excel
        Args:
            lms: The LMS instance containing courses
            filename: Optional filename, if None generates automatic filename
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            lms_name = getattr(lms, 'name', 'LMS')
            safe_name = Utils.safe_filename(lms_name)
            filename = f"Courses_{safe_name}_{timestamp}.xlsx"
        
        self.excel_helper.create_workbook()
        
        # Headers
        headers = ["Course ID", "Course Name", "Category", "Enrolled Users", "User Groups"]
        self.excel_helper.add_headers(headers)
        
        # Export courses
        courses = getattr(lms, 'courses', [])
        for course in courses:
            course_id = getattr(course, 'id', '')
            course_name = getattr(course, 'name', '')
            
            # Get category name
            category = getattr(course, 'category', None)
            category_name = getattr(category, 'name', '') if category else ''
            
            # Count users and groups
            enrolled_users = getattr(course, 'enrolled_users', [])
            user_groups = getattr(course, 'user_groups', [])
            
            row_data = [
                course_id,
                course_name,
                category_name,
                len(enrolled_users),
                len(user_groups)
            ]
            self.excel_helper.add_row(row_data)
        
        self.excel_helper.auto_fit_columns()
        self.excel_helper.save_workbook(filename)
    
    def export_users_to_excel(self, lms: ILMS, filename: str = None):
        """
        Export all users from LMS to Excel
        Args:
            lms: The LMS instance containing users
            filename: Optional filename, if None generates automatic filename
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            lms_name = getattr(lms, 'name', 'LMS')
            safe_name = Utils.safe_filename(lms_name)
            filename = f"Users_{safe_name}_{timestamp}.xlsx"
        
        self.excel_helper.create_workbook()
        
        # Headers
        headers = ["User ID", "First Name", "Last Name", "Email", "Full Name", "Roles", "Courses"]
        self.excel_helper.add_headers(headers)
        
        # Collect all users from all courses
        all_users = {}
        courses = getattr(lms, 'courses', [])
        
        for course in courses:
            enrolled_users = getattr(course, 'enrolled_users', [])
            for user in enrolled_users:
                user_id = getattr(user, 'id', '')
                if user_id not in all_users:
                    all_users[user_id] = {
                        'user': user,
                        'courses': []
                    }
                all_users[user_id]['courses'].append(course.name)
        
        # Export users
        for user_data in all_users.values():
            user = user_data['user']
            user_courses = ', '.join(user_data['courses'])
            
            row_data = [
                getattr(user, 'id', ''),
                getattr(user, 'first_name', ''),
                getattr(user, 'last_name', ''),
                getattr(user, 'email', ''),
                getattr(user, 'full_name', ''),
                ', '.join(getattr(user, 'roles', [])),
                user_courses
            ]
            self.excel_helper.add_row(row_data)
        
        self.excel_helper.auto_fit_columns()
        self.excel_helper.save_workbook(filename)
    
    def export_categories_to_excel(self, lms: ILMS, filename: str = None):
        """
        Export all categories from LMS to Excel
        Args:
            lms: The LMS instance containing categories
            filename: Optional filename, if None generates automatic filename
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            lms_name = getattr(lms, 'name', 'LMS')
            safe_name = Utils.safe_filename(lms_name)
            filename = f"Categories_{safe_name}_{timestamp}.xlsx"
        
        self.excel_helper.create_workbook()
        
        # Headers
        headers = ["Category ID", "Category Name", "Courses Count", "Course Names"]
        self.excel_helper.add_headers(headers)
        
        # Export categories
        categories = getattr(lms, 'categories', [])
        for category in categories:
            category_id = getattr(category, 'id', '')
            category_name = getattr(category, 'name', '')
            courses = getattr(category, 'courses', [])
            course_names = ', '.join([getattr(course, 'name', '') for course in courses])
            
            row_data = [
                category_id,
                category_name,
                len(courses),
                course_names
            ]
            self.excel_helper.add_row(row_data)
        
        self.excel_helper.auto_fit_columns()
        self.excel_helper.save_workbook(filename)
    
    def generate_course_summary_report(self, course: ICourse) -> str:
        """
        Generate a text summary report for a course
        Args:
            course: The course to generate report for
        Returns:
            Formatted report text
        """
        report_lines = []
        report_lines.append(f"Course Summary Report")
        report_lines.append("=" * 50)
        report_lines.append(f"Course Name: {getattr(course, 'name', '')}")
        report_lines.append(f"Course ID: {getattr(course, 'id', '')}")
        
        # Category information
        category = getattr(course, 'category', None)
        if category:
            report_lines.append(f"Category: {getattr(category, 'name', '')}")
        
        report_lines.append("")
        
        # User statistics
        enrolled_users = getattr(course, 'enrolled_users', [])
        user_groups = getattr(course, 'user_groups', [])
        
        report_lines.append(f"Total Enrolled Users: {len(enrolled_users)}")
        report_lines.append(f"User Groups: {len(user_groups)}")
        
        if user_groups:
            report_lines.append("")
            report_lines.append("User Groups:")
            for group in user_groups:
                group_name = getattr(group, 'group_name', '')
                users_in_group = getattr(group, 'users_in_group', [])
                report_lines.append(f"  - {group_name}: {len(users_in_group)} users")
        
        report_lines.append("")
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(report_lines)
    
    def generate_lms_summary_report(self, lms: ILMS) -> str:
        """
        Generate a text summary report for an LMS
        Args:
            lms: The LMS instance to generate report for
        Returns:
            Formatted report text
        """
        report_lines = []
        report_lines.append(f"LMS Summary Report")
        report_lines.append("=" * 50)
        report_lines.append(f"LMS Name: {getattr(lms, 'name', '')}")
        report_lines.append(f"LMS Host: {getattr(lms, 'host', '')}")
        report_lines.append("")
        
        # Statistics
        categories = getattr(lms, 'categories', [])
        courses = getattr(lms, 'courses', [])
        enrolled_courses = getattr(lms, 'enrolled_courses', [])
        
        report_lines.append(f"Total Categories: {len(categories)}")
        report_lines.append(f"Total Courses: {len(courses)}")
        report_lines.append(f"Enrolled Courses: {len(enrolled_courses)}")
        
        # Count total users
        total_users = 0
        for course in courses:
            enrolled_users = getattr(course, 'enrolled_users', [])
            total_users += len(enrolled_users)
        
        report_lines.append(f"Total Users: {total_users}")
        report_lines.append("")
        
        # Current user information
        current_user = getattr(lms, 'user', None)
        if current_user:
            report_lines.append(f"Current User: {getattr(current_user, 'full_name', '')}")
            report_lines.append(f"User Email: {getattr(current_user, 'email', '')}")
        
        report_lines.append("")
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(report_lines)


# Global reports helper instance
_global_reports_helper: Optional[ReportsHelper] = None


def get_reports_helper() -> ReportsHelper:
    """Get the global reports helper instance"""
    global _global_reports_helper
    if _global_reports_helper is None:
        _global_reports_helper = ReportsHelper()
    return _global_reports_helper


# Backward compatibility functions
def ExportToExcel(course: ICourse):
    """Export course to Excel (backward compatibility)"""
    get_reports_helper().export_course_to_excel(course)


def ExportToExcelCourses(lms: ILMS):
    """Export courses to Excel (backward compatibility)"""
    get_reports_helper().export_courses_to_excel(lms)
