#!/usr/bin/env python3
"""
Reset admin password for Moodle Manager System
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.system.system_user_manager import SystemUserManager

def reset_admin_password():
    """Reset admin password to a known default"""
    system_user_manager = SystemUserManager()
    
    # Get admin user
    admin_user = system_user_manager.get_user_by_username('admin')
    
    if not admin_user:
        print("Admin user not found. Creating new admin user...")
        success = system_user_manager.create_user(
            username='admin',
            email='admin@moodle.local',
            password='admin123',
            full_name='System Administrator',
            role='admin',
            is_admin=True
        )
        
        if success:
            print("✅ New admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("❌ Failed to create admin user")
        return
    
    # Reset existing admin password
    success = system_user_manager.change_password(admin_user['id'], 'admin123')
    
    if success:
        print("✅ Admin password reset successfully!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("❌ Failed to reset admin password")

if __name__ == "__main__":
    reset_admin_password()
