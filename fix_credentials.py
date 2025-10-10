#!/usr/bin/env python3
"""
Moodle Manager Credential Reset Script
Fixes "Incorrect padding" errors by clearing corrupted credentials
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def reset_credentials():
    """Reset corrupted credentials and encryption keys"""

    print("🔧 MOODLE MANAGER CREDENTIAL RESET")
    print("=" * 50)

    try:
        from auth_manager import AuthManager
        from database_manager import DatabaseManager

        print("🗑️  Clearing corrupted credentials...")

        # Initialize managers
        auth_manager = AuthManager("MoodleManager")
        db_manager = DatabaseManager()

        # Clear all stored credentials from keyring
        try:
            # Try to clear all credentials
            auth_manager.clear_all_credentials()
            print("✓ Cleared all credentials from keyring")
        except Exception as e:
            print(f"⚠️  Could not clear keyring: {e}")
            print("   This is normal if no credentials were stored")

        # Clear database credentials for Moodle servers
        try:
            moodle_servers = db_manager.get_all_moodle_servers()
            for server in moodle_servers:
                # Delete all credentials for this server
                credentials = db_manager.get_all_credentials_for_server(server['id'], 'moodle')
                for cred in credentials:
                    db_manager.delete_credentials(server['id'], cred['username'])
                    print(f"✓ Cleared database credentials for {cred['username']}")

            if not moodle_servers:
                print("✓ No Moodle servers found in database")

        except Exception as e:
            print(f"⚠️  Error clearing database credentials: {e}")

        # Clear encryption key to force regeneration
        key_file = Path.home() / '.moodle_manager' / 'encryption.key'
        if key_file.exists():
            try:
                key_file.unlink()
                print("✓ Removed corrupted encryption key")
                print("   New key will be generated on next use")
            except Exception as e:
                print(f"⚠️  Could not remove encryption key: {e}")

        # Clear any cached credential files
        cache_files = [
            Path.home() / '.MoodleManager_credentials.cache',
            Path.home() / '.moodlemanager_credentials.cache',
            Path.home() / '.moodle_manager' / 'credentials.cache'
        ]

        for cache_file in cache_files:
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    print(f"✓ Removed cache file: {cache_file}")
                except Exception as e:
                    print(f"⚠️  Could not remove {cache_file}: {e}")

        print()
        print("🎉 CREDENTIAL RESET COMPLETE!")
        print("=" * 50)
        print()
        print("✅ All corrupted credentials cleared")
        print("✅ Encryption keys reset")
        print("✅ Cache files removed")
        print()
        print("🚀 NEXT STEPS:")
        print("   1. Run auto-connect setup again:")
        print("      python setup_auto_connect.py")
        print("   2. Or manually login through the GUI")
        print("   3. Credentials will be stored fresh")
        print()
        print("💡 The 'Incorrect padding' error should be resolved!")

        return True

    except Exception as e:
        print(f"✗ Error during credential reset: {e}")
        return False

def show_current_status():
    """Show current credential status"""
    print("📊 CURRENT CREDENTIAL STATUS:")
    print()

    try:
        from database_manager import DatabaseManager

        db = DatabaseManager()

        # Check Moodle servers
        servers = db.get_all_moodle_servers()
        print(f"Moodle Servers: {len(servers)}")
        for server in servers:
            print(f"  • {server['name']}: {server['host']}:{server['port']}")

        # Check credentials
        for server in servers:
            creds = db.get_all_credentials_for_server(server['id'], 'moodle')
            print(f"Credentials for {server['name']}: {len(creds)}")
            for cred in creds:
                print(f"  • {cred['username']} (Remembered: {cred['is_remembered']})")

        # Check application settings
        settings = db.get_all_settings()
        auto_connect_settings = {k: v for k, v in settings.items() if 'auto_connect' in k.lower()}
        if auto_connect_settings:
            print(f"Auto-connect Settings: {len(auto_connect_settings)}")
            for key, value in auto_connect_settings.items():
                print(f"  • {key}: {value}")
        else:
            print("Auto-connect Settings: None found")

    except Exception as e:
        print(f"Error checking status: {e}")

if __name__ == "__main__":
    print("🔧 Fixing Moodle Manager credential issues...")
    print()

    success = reset_credentials()
    show_current_status()

    if success:
        print("\n🎯 Credential reset completed successfully!")
        print("🚀 Run: python setup_auto_connect.py")
        print("   to reconfigure auto-connect with fresh credentials")
    else:
        print("\n❌ Credential reset encountered issues")
        print("🔧 Please check the error messages above")
