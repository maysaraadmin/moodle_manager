#!/usr/bin/env python3
"""
Comprehensive fix for all import issues after reorganization
"""

import os
import re
import sys

def fix_file_imports(file_path):
    """Fix all import issues in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Add missing os/sys imports before project_root usage
        if 'project_root = os.path.dirname' in content:
            lines = content.split('\n')
            new_lines = []
            added_os_sys = False
            
            for i, line in enumerate(lines):
                # Add os/sys imports before project_root if not already present
                if not added_os_sys and 'project_root = os.path.dirname' in line:
                    # Check if os and sys are already imported above
                    has_os = any('import os' in prev_line for prev_line in lines[:i])
                    has_sys = any('import sys' in prev_line for prev_line in lines[:i])
                    
                    if not has_os:
                        new_lines.append('import os')
                    if not has_sys:
                        new_lines.append('import sys')
                    if not has_os or not has_sys:
                        new_lines.append('')
                    
                    new_lines.append(line)
                    added_os_sys = True
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
        
        # Fix 2: Update old import paths
        old_imports = {
            'from utils.helpers.': 'from utils.helpers.',
            'from utils.forms.': 'from utils.forms.',
            'from ui.views.': 'from ui.views.',
            'from ui.dialogs.': 'from ui.dialogs.',
            'from utils.helpers import browser': 'from utils.helpers from utils.helpers import browser',
            'from utils.helpers import csv_helper': 'from utils.helpers from utils.helpers import csv_helper',
            'from utils.helpers import excel': 'from utils.helpers from utils.helpers import excel',
            'from utils.helpers import reports': 'from utils.helpers from utils.helpers import reports',
            'from utils.helpers import images': 'from utils.helpers from utils.helpers import images',
            'from utils.helpers import logger': 'from utils.helpers from utils.helpers import logger',
            'from utils.helpers import constants': 'from utils.helpers from utils.helpers import constants',
            'from utils.helpers import form_factory': 'from utils.helpers from utils.helpers import form_factory',
            'from utils.helpers import rtti': 'from utils.helpers from utils.helpers import rtti',
            'from utils.helpers import utils': 'from utils.helpers from utils.helpers import utils',
            'from utils.config.config_manager import': 'from utils.config.config_manager import',
            'from utils.progress.progress_manager import': 'from utils.progress.progress_manager import',
            'from utils.error_handling.error_handler import': 'from utils.error_handling.error_handler import',
            'from utils.error_handling.error_handling import': 'from utils.error_handling.error_handling import',
            'from utils.validation.connection_validator import': 'from utils.validation.connection_validator import',
            'from services.moodle.moodle_rest import': 'from services.moodle.moodle_rest import',
            'from services.moodle.moodle_threads import': 'from services.moodle.moodle_threads import',
            'from services.moodle.lms_interface import': 'from services.moodle.lms_interface import',
            'from api_new.endpoints.routes import': 'from api_new.endpoints.routes import',
            'from api.middleware.auth_middleware import': 'from api.middleware.auth_middleware import',
            'from api_new.fastapi_manager import': 'from api_new.fastapi_manager import',
            'from core.system.system_user_manager import': 'from core.system.system_user_manager import',
            'from core.system.system_login_dialog import': 'from core.system.system_login_dialog import',
            'from core.system.system_profile_dialog import': 'from core.system.system_profile_dialog import',
            'from core.database.database_manager import': 'from core.database.database_manager import',
            'from core.auth.auth_manager import': 'from core.auth.auth_manager import',
            'from core.auth.credential_manager import': 'from core.auth.credential_manager import',
            'from core.auth.user_session_manager import': 'from core.auth.user_session_manager import',
            'from core.data_models import': 'from core.data_models import',
            'from ui.main.main_window import': 'from ui.main.main_window import',
            'from ui.main.moodle_info_page import': 'from ui.main.moodle_info_page import',
            'from ui.dialogs.login_dialog import': 'from ui.dialogs.login_dialog import',
            'from ui.dialogs.about_dialog import': 'from ui.dialogs.about_dialog import',
            'from ui.dialogs.settings_dialog import': 'from ui.dialogs.settings_dialog import',
            'from ui.dialogs.lms_dialog import': 'from ui.dialogs.lms_dialog import',
            'from ui.dialogs.user_profile_dialog import': 'from ui.dialogs.user_profile_dialog import',
            'from ui.dialogs.user_grades_dialog import': 'from ui.dialogs.user_grades_dialog import',
            'from ui.dialogs.course_content_dialog import': 'from ui.dialogs.course_content_dialog import',
            'from ui.dialogs.course_users_dialog import': 'from ui.dialogs.course_users_dialog import',
            'from ui.views.network_tree import': 'from ui.views.network_tree import',
            'from ui.views.lms_tree import': 'from ui.views.lms_tree import',
            'from ui.views.courses_tree import': 'from ui.views.courses_tree import',
            'from ui.views.users_tree import': 'from ui.views.users_tree import',
            'from ui.views.course_category_tree import': 'from ui.views.course_category_tree import',
            'from ui.views.course_content_tree import': 'from ui.views.course_content_tree import',
            'from ui.views.course_users_tree import': 'from ui.views.course_users_tree import',
            'from ui.views.user_courses_tree import': 'from ui.views.user_courses_tree import',
            'from ui.views.custom_tree import': 'from ui.views.custom_tree import',
            'from utils.forms.user_form import': 'from utils.forms.user_form import',
            'from utils.forms.course_form import': 'from utils.forms.course_form import',
            'from utils.forms.category_form import': 'from utils.forms.category_form import',
            'from utils.forms.content_form import': 'from utils.forms.content_form import',
            'from utils.forms.module_form import': 'from utils.forms.module_form import',
            'from utils.forms.section_form import': 'from utils.forms.section_form import',
        }
        
        for old_import, new_import in old_imports.items():
            content = content.replace(old_import, new_import)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing imports in {file_path}: {e}")
        return False

def process_directory(directory):
    """Process all Python files in a directory"""
    fixed_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Skip __pycache__ directories
                if '__pycache__' in file_path:
                    continue
                
                # Fix imports
                if fix_file_imports(file_path):
                    fixed_files.append(file_path)
                    print(f"Fixed imports: {file_path}")
    
    return fixed_files

def main():
    """Main function"""
    print("Fixing all import issues...")
    
    # Get project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Process all Python files
    fixed_files = process_directory(project_root)
    
    if fixed_files:
        print(f"\nFixed {len(fixed_files)} files:")
        for file_path in fixed_files:
            print(f"  - {file_path}")
    else:
        print("No files needed fixing.")
    
    print("\nComprehensive import fix completed!")

if __name__ == "__main__":
    main()
