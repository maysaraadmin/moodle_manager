#!/usr/bin/env python3
"""
Test script for enhanced login system with connection validation
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from login_dialog import LoginDialog
from auth_manager import AuthManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_enhanced_login():
    """Test the enhanced login dialog"""
    print("Testing Enhanced Login System...")
    
    app = QApplication(sys.argv)
    
    # Create auth manager
    auth_manager = AuthManager("MoodleManager")
    
    # Create login dialog
    login_dialog = LoginDialog(auth_manager=auth_manager)
    
    # Connect signals
    def on_login_successful(connection_details):
        print(f"Login successful: {connection_details}")
        print("Enhanced login test completed successfully!")
        
    def on_login_failed(error_message):
        print(f"Login failed: {error_message}")
        print("Enhanced login test failed!")
    
    login_dialog.login_successful.connect(on_login_successful)
    login_dialog.login_failed.connect(on_login_failed)
    
    # Show dialog
    result = login_dialog.exec_()
    
    if result == LoginDialog.Accepted:
        print("Dialog accepted - login was successful")
    else:
        print("Dialog rejected - login was cancelled or failed")
    
    app.quit()

if __name__ == "__main__":
    test_enhanced_login()
