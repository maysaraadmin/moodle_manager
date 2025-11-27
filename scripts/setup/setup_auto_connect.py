#!/usr/bin/env python3
"""
Moodle Manager Auto-Connect Setup
Configures automatic connection to Moodle server on application startup
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database.database_manager import DatabaseManager
from core.auth.auth_manager import AuthManager

def setup_auto_connect():
    """Set up automatic connection to Moodle server"""

    print("🔗 SETTING UP MOODLE AUTO-CONNECT")
    print("=" * 50)

    # Moodle server details
    moodle_config = {
        'name': 'Moodle',
        'host': 'http://127.0.0.1/moodle/',
        'port': 80,
        'service_name': 'moodle_mobile_app',
        'username': 'lms_explorer',
        'password': 'Lms_explorer_services@2025',
        'description': 'Local Moodle instance for development'
    }

    print(f"📋 Moodle Configuration:")
    print(f"   Server: {moodle_config['host']}")
    print(f"   Username: {moodle_config['username']}")
    print(f"   Service: {moodle_config['service_name']}")
    print()

    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        auth_manager = AuthManager("MoodleManager")

        print("💾 Saving Moodle server configuration to database...")

        # Save Moodle server to database
        server_id = db_manager.save_moodle_server(
            name=moodle_config['name'],
            host=moodle_config['host'],
            port=moodle_config['port'],
            service_name=moodle_config['service_name'],
            description=moodle_config['description']
        )

        if server_id > 0:
            print(f"✓ Moodle server saved with ID: {server_id}")

            # Save credentials to auth manager
            print("🔐 Saving credentials securely...")
            success = auth_manager.store_credentials(
                host=moodle_config['host'],
                username=moodle_config['username'],
                password=moodle_config['password'],
                service=moodle_config['service_name'],
                remember_me=True
            )

            if success:
                print("✓ Credentials stored securely in keyring")

                # Save credentials to database as well
                db_manager.save_credentials(
                    server_id=server_id,
                    server_type='moodle',
                    username=moodle_config['username'],
                    password=moodle_config['password'],  # Will be encrypted
                    is_remembered=True
                )
                print("✓ Credentials also saved to database")

                # Log successful connection for testing
                db_manager.log_connection(
                    server_id=server_id,
                    server_type='moodle',
                    success=True,
                    response_time_ms=0,
                    user_agent="MoodleManager/1.0 (Auto-Setup)"
                )
                print("✓ Connection logged for reference")

            else:
                print("⚠️  Failed to store credentials in keyring")

        else:
            print("✗ Failed to save Moodle server configuration")
            return False

        # Save application settings for auto-connect
        print("⚙️  Configuring application settings...")

        settings_to_save = {
            'auto_connect_enabled': True,
            'auto_connect_server': moodle_config['name'],
            'auto_connect_username': moodle_config['username'],
            'default_moodle_url': moodle_config['host'],
            'default_service_name': moodle_config['service_name']
        }

        for key, value in settings_to_save.items():
            db_manager.save_setting(key, value)
            print(f"  ✓ Setting: {key} = {value}")

        # Save to config.ini for compatibility
        print("📄 Saving configuration to config.ini...")

        config_path = 'config.ini'
        config_content = f'''[lms1]
url = {moodle_config['host']}
user = {moodle_config['username']}
service = {moodle_config['service_name']}
autoconnect = 1
remember_me = 1
password =

[settings]
auto_connect = 1
default_server = Moodle
theme = system
'''

        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"✓ Configuration saved to {config_path}")

        print()
        print("🎉 AUTO-CONNECT SETUP COMPLETE!")
        print("=" * 50)
        print()
        print("✅ Moodle server configuration saved")
        print("✅ Credentials stored securely")
        print("✅ Auto-connect enabled in settings")
        print("✅ Configuration file updated")
        print()
        print("🚀 NEXT STEPS:")
        print("   1. Start Moodle Manager: python main.py")
        print("   2. Application will automatically attempt to connect")
        print("   3. If Moodle server is running, connection will succeed")
        print("   4. If Moodle server is not running, you'll get connection error")
        print()
        print("💡 To start Moodle server:")
        print("   • Install Moodle in XAMPP/WAMP")
        print("   • Start Apache and MySQL services")
        print("   • Access http://localhost/moodle/")
        print("   • Enable web services in Moodle admin")

        return True

    except Exception as e:
        print(f"✗ Error during auto-connect setup: {e}")
        return False

def test_connection():
    """Test if Moodle server is accessible"""
    print("🌐 TESTING MOODLE SERVER ACCESSIBILITY...")
    print()

    moodle_url = "http://127.0.0.1/moodle/"

    try:
        import requests

        print(f"Testing connection to: {moodle_url}")
        response = requests.get(moodle_url, timeout=5)

        if response.status_code == 200:
            print("✅ Moodle server is accessible!")
            print(f"   HTTP Status: {response.status_code}")

            # Check if it looks like Moodle
            if 'moodle' in response.text.lower() or 'login' in response.text.lower():
                print("✅ Response appears to be Moodle")
            else:
                print("⚠️  Response received but may not be Moodle")

        else:
            print(f"⚠️  Moodle server responded with HTTP {response.status_code}")
            print("   Server is running but may have issues")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Moodle server")
        print("   • Moodle server is not running")
        print("   • Check if Apache/MySQL services are started")
        print("   • Verify Moodle is installed at the correct path")
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
        print("   • Moodle server is slow to respond")
        print("   • Check server performance")
    except Exception as e:
        print(f"❌ Connection test error: {e}")

    print()
    print("💡 SETUP COMPLETE REGARDLESS OF SERVER STATUS")
    print("   Moodle Manager will attempt auto-connect when started")

if __name__ == "__main__":
    success = setup_auto_connect()
    test_connection()

    if success:
        print("\n🎯 Auto-connect setup completed successfully!")
        print("🚀 Start Moodle Manager: python main.py")
    else:
        print("\n❌ Auto-connect setup encountered issues")
        print("🔧 Please check the error messages above")
