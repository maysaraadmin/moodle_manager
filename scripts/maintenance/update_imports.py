#!/usr/bin/env python3
"""
Update import statements after project reorganization
"""

import os
import re
import sys
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_MAPPING = {
    # Core modules
    'from core.system.system_user_manager import': 'from core.system.system_user_manager import',
    'from core.system.system_login_dialog import': 'from core.system.system_login_dialog import',
    'from core.system.system_profile_dialog import': 'from core.system.system_profile_dialog import',
    'from core.database.database_manager import': 'from core.database.database_manager import',
    'from core.auth.auth_manager import': 'from core.auth.auth_manager import',
    'from core.auth.credential_manager import': 'from core.auth.credential_manager import',
    'from core.auth.user_session_manager import': 'from core.auth.user_session_manager import',
    'from core.data_models import': 'from core.data_models import',
    
    # UI modules
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
    
    # Utils modules
    'from utils.config.config_manager import': 'from utils.config.config_manager import',
    'from utils.progress.progress_manager import': 'from utils.progress.progress_manager import',
    'from utils.error_handling.error_handler import': 'from utils.error_handling.error_handler import',
    'from utils.error_handling.error_handling import': 'from utils.error_handling.error_handling import',
    'from utils.validation.connection_validator import': 'from utils.validation.connection_validator import',
    'from utils.helpers.browser import': 'from utils.helpers.browser import',
    'from utils.helpers.csv_helper import': 'from utils.helpers.csv_helper import',
    'from utils.helpers.excel import': 'from utils.helpers.excel import',
    'from utils.helpers.reports import': 'from utils.helpers.reports import',
    'from utils.helpers.images import': 'from utils.helpers.images import',
    'from utils.helpers.logger import': 'from utils.helpers.logger import',
    'from utils.helpers.constants import': 'from utils.helpers.constants import',
    'from utils.helpers.form_factory import': 'from utils.helpers.form_factory import',
    'from utils.helpers.rtti import': 'from utils.helpers.rtti import',
    'from utils.helpers.utils import': 'from utils.helpers.utils import',
    
    # Services modules
    'from services.moodle.moodle_rest import': 'from services.moodle.moodle_rest import',
    'from services.moodle.moodle_threads import': 'from services.moodle.moodle_threads import',
    'from services.moodle.lms_interface import': 'from services.moodle.lms_interface import',
    
    # API modules
    'from api_new.endpoints.routes import': 'from api_new.endpoints.routes import',
    'from api.middleware.auth_middleware import': 'from api.middleware.auth_middleware import',
    'from api_new.fastapi_manager import': 'from api_new.fastapi_manager import',
    
    # Form modules
    'from utils.forms.user_form import': 'from utils.forms.user_form import',
    'from utils.forms.course_form import': 'from utils.forms.course_form import',
    'from utils.forms.category_form import': 'from utils.forms.category_form import',
    'from utils.forms.content_form import': 'from utils.forms.content_form import',
    'from utils.forms.module_form import': 'from utils.forms.module_form import',
    'from utils.forms.section_form import': 'from utils.forms.section_form import',
}

def add_project_root_import(file_path):
    """Add project root import to Python files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if project root import already exists
        if 'project_root = os.path.dirname(os.path.dirname(os.path.dirname(' in content:
            return False
        
        # Find the first import line and add project root before it
        lines = content.split('\n')
        new_lines = []
        added = False
        
        for line in lines:
            if not added and (line.startswith('import ') or line.startswith('from ')):
                # Add project root import before the first import
                new_lines.extend([
                    "# Add the project root to the Python path",
                    "project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
                    "sys.path.insert(0, project_root)",
                    ""
                ])
                added = True
            new_lines.append(line)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        return True
    except Exception as e:
        print(f"Error adding project root import to {file_path}: {e}")
        return False

def update_imports_in_file(file_path):
    """Update imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update imports according to mapping
        for old_import, new_import in IMPORT_MAPPING.items():
            content = content.replace(old_import, new_import)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error updating imports in {file_path}: {e}")
        return False

def process_directory(directory):
    """Process all Python files in a directory"""
    updated_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Skip __pycache__ directories
                if '__pycache__' in file_path:
                    continue
                
                # Add project root import
                if add_project_root_import(file_path):
                    updated_files.append(file_path)
                    print(f"Added project root import: {file_path}")
                
                # Update imports
                if update_imports_in_file(file_path):
                    updated_files.append(file_path)
                    print(f"Updated imports: {file_path}")
    
    return updated_files

def main():
    """Main function"""
    print("Updating imports after project reorganization...")
    
    # Get project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Process all Python files
    updated_files = process_directory(project_root)
    
    print(f"\nUpdated {len(updated_files)} files:")
    for file_path in updated_files:
        print(f"  - {file_path}")
    
    print("\nImport update completed!")

if __name__ == "__main__":
    main()
