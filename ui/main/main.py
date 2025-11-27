#!/usr/bin/env python3
"""
LMS Explorer - PyQt5 Application
A Learning Management System interface for Moodle
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Enable high DPI scaling before creating QApplication
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

from ui.main.main_window import MainWindow
from core.system.system_login_dialog import SystemLoginDialog
from ui.dialogs.login_dialog import LoginDialog
from core.auth.auth_manager import AuthManager
from core.auth.user_session_manager import UserSessionManager
from core.system.system_user_manager import SystemUserManager

def main():
    """Main entry point for the LMS Explorer application"""
    app = QApplication(sys.argv)
    
    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Application started")
    
    # Set application information
    app.setApplicationName("LMS Explorer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("LMS Explorer")
    
    # Initialize managers
    auth_manager = AuthManager("MoodleManager")
    session_manager = UserSessionManager("MoodleManager")
    system_user_manager = SystemUserManager()
    
    # System authentication first
    system_login_dialog = SystemLoginDialog()
    
    # Try auto-login for system user
    # (Could implement system-level remember me functionality)
    
    # Show system login dialog
    system_login_dialog.login_successful.connect(
        lambda system_data: on_system_login_success(system_data, app, auth_manager, session_manager)
    )
    system_login_dialog.login_failed.connect(
        lambda error: on_system_login_failed(error)
    )
    
    result = system_login_dialog.exec_()
    
    # If system login was rejected (closed), exit application
    if result == system_login_dialog.Rejected:
        sys.exit(0)
    
    # Run the application
    sys.exit(app.exec_())

def on_system_login_success(system_data, app, auth_manager, session_manager):
    """Handle successful system login and show dashboard"""
    try:
        # Extract system user data
        user_data = system_data.get('user', {})
        session_token = system_data.get('session_token', '')
        
        print(f"System user logged in: {user_data.get('username')}")
        
        # Show main window immediately after system login
        main_window = MainWindow()
        main_window.set_system_user(user_data, session_token)
        main_window.show()
        
        # Optionally try Moodle auto-login in background
        # but don't require it for dashboard access
        # DISABLED: Focus on system login first
        """
        try:
            stored_creds = auth_manager.get_all_credentials()
            if stored_creds:
                # Try auto-login with Moodle credentials in background
                moodle_login_dialog = LoginDialog(auth_manager=auth_manager)
                for host, cred_data in list(stored_creds.items())[:1]:
                    if moodle_login_dialog.auto_login(host, cred_data.get('username', '')):
                        # Moodle auto-login successful
                        main_window.on_login_successful({
                            'host': host,
                            'username': cred_data.get('username', ''),
                            'service': cred_data.get('service', 'moodle_mobile_app'),
                            'password': cred_data.get('password', ''),
                            'remember_me': cred_data.get('remember_me', False)
                        })
                        break
        except Exception as e:
            print(f"Moodle auto-login failed (non-critical): {e}")
            # Don't show error to user - Moodle login is optional
        """
            
    except Exception as e:
        QMessageBox.critical(None, "System Login Error", f"Failed to load main window: {str(e)}")
        app.quit()

def on_moodle_login_success(connection_details, main_window):
    """Handle successful Moodle login"""
    try:
        main_window.on_login_successful(connection_details)
        main_window.show()
    except Exception as e:
        QMessageBox.critical(None, "Moodle Login Error", f"Failed to process Moodle login: {str(e)}")

def on_system_login_failed(error_message):
    """Handle system login failure"""
    QMessageBox.warning(None, "System Login Failed", f"System login failed: {error_message}")

def on_moodle_login_failed(error_message):
    """Handle Moodle login failure"""
    QMessageBox.warning(None, "Moodle Login Failed", f"Moodle login failed: {error_message}")

if __name__ == "__main__":
    main()
