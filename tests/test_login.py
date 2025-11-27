#!/usr/bin/env python3
"""
Test the complete system login flow
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

from PyQt5.QtWidgets import QApplication
from core.system.system_login_dialog import SystemLoginDialog

def test_login():
    """Test the complete login flow"""
    app = QApplication(sys.argv)
    
    # Create login dialog
    login_dialog = SystemLoginDialog()
    
    # Test successful login
    login_dialog.username_input.setText('admin')
    login_dialog.password_input.setText('admin123')
    
    print("Testing login with credentials: admin/admin123")
    
    # Attempt login
    login_dialog.attempt_login()
    
    # Check if login was successful
    if login_dialog.current_user:
        print("✅ Login successful!")
        print(f"User: {login_dialog.current_user['username']}")
        print(f"Session token: {login_dialog.session_token[:20] if login_dialog.session_token else 'None'}...")
        
        # Test session validation
        session_data = login_dialog.system_user_manager.validate_session(login_dialog.session_token)
        if session_data:
            print("✅ Session validation successful!")
        else:
            print("❌ Session validation failed")
    else:
        print("❌ Login failed")
    
    app.quit()

if __name__ == "__main__":
    test_login()
