#!/usr/bin/env python3
"""
Setup script for Moodle Manager System Users
Creates the initial system administrator account
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import sys
import os
import getpass

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.system.system_user_manager import SystemUserManager


def create_admin_user():
    """Create the initial administrator user"""
    print("=== Moodle Manager System Setup ===")
    print("Creating initial system administrator account...")
    print()
    
    # Get user input
    username = input("Enter admin username: ").strip()
    if not username:
        print("Username is required!")
        return False
    
    email = input("Enter admin email: ").strip()
    if not email or '@' not in email:
        print("Valid email is required!")
        return False
    
    full_name = input("Enter admin full name: ").strip()
    if not full_name:
        print("Full name is required!")
        return False
    
    # Get password (hidden input)
    password = getpass.getpass("Enter admin password: ")
    if not password:
        print("Password is required!")
        return False
    
    if len(password) < 6:
        print("Password must be at least 6 characters!")
        return False
    
    confirm_password = getpass.getpass("Confirm admin password: ")
    if password != confirm_password:
        print("Passwords do not match!")
        return False
    
    # Create system user manager
    system_user_manager = SystemUserManager()
    
    # Create admin user
    success = system_user_manager.create_user(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        role='admin',
        is_admin=True
    )
    
    if success:
        print()
        print("✅ System administrator created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Full Name: {full_name}")
        print()
        print("You can now login to Moodle Manager with these credentials.")
        return True
    else:
        print()
        print("❌ Failed to create administrator account!")
        print("Username or email may already exist.")
        return False


def list_users():
    """List all system users"""
    system_user_manager = SystemUserManager()
    users = system_user_manager.get_all_users()
    
    print("=== System Users ===")
    if not users:
        print("No users found.")
        return
    
    for user in users:
        status = "Active" if user['is_active'] else "Inactive"
        admin = "Admin" if user['is_admin'] else "User"
        print(f"- {user['username']} ({user['email']}) - {admin} - {status}")


def show_stats():
    """Show system statistics"""
    system_user_manager = SystemUserManager()
    stats = system_user_manager.get_system_stats()
    
    print("=== System Statistics ===")
    print(f"Active Users: {stats.get('active_users', 0)}")
    print(f"Total Users: {stats.get('total_users', 0)}")
    print(f"Active Sessions: {stats.get('active_sessions', 0)}")
    print(f"Total Sessions: {stats.get('total_sessions', 0)}")


def main():
    """Main setup menu"""
    while True:
        print()
        print("=== Moodle Manager System Setup ===")
        print("1. Create Administrator Account")
        print("2. List Users")
        print("3. Show System Statistics")
        print("4. Exit")
        print()
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            create_admin_user()
        elif choice == '2':
            list_users()
        elif choice == '3':
            show_stats()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
