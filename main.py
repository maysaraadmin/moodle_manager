#!/usr/bin/env python3
"""
LMS Explorer - PyQt5 Application
A Learning Management System interface for Moodle
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Enable high DPI scaling before creating QApplication
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

from main_window import MainWindow

def main():
    """Main entry point for the LMS Explorer application"""
    app = QApplication(sys.argv)
    
    # Set application information
    app.setApplicationName("LMS Explorer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("LMS Explorer")
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
