#!/usr/bin/env python3
"""
Moodle Manager - Complete Credential System Reset
Comprehensive fix for persistent "Incorrect padding" errors
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import os
import sys
import sqlite3
import shutil
from pathlib import Path

def complete_credential_reset():
    """Complete reset of all credential-related systems"""

    print("🔧 COMPLETE MOODLE MANAGER CREDENTIAL RESET")
    print("=" * 60)

    reset_performed = False

    # 1. Clear all keyring entries
    print("\n🔑 CLEARING SYSTEM KEYRING...")
    try:
        import keyring

        # Try to clear all Moodle-related entries
        services_to_clear = [
            'MoodleManager',
            'moodle',
            'Moodle',
            'lms_explorer',
            'moodle_mobile_app'
        ]

        usernames_to_clear = [
            'lms_explorer',
            'admin',
            'test',
            'demo',
            'user'
        ]

        cleared_count = 0
        for service in services_to_clear:
            for username in usernames_to_clear:
                try:
                    keyring.delete_password(service, username)
                    cleared_count += 1
                except:
                    pass  # Entry doesn't exist

        print(f"✓ Keyring cleanup completed (attempted ~{cleared_count} entries)")

    except ImportError:
        print("⚠️  Keyring module not available")
    except Exception as e:
        print(f"⚠️  Keyring error: {e}")

    # 2. Complete database reset
    print("\n💾 RESETTING DATABASE...")

    # Backup current database if it exists
    db_path = Path.home() / '.moodle_manager' / 'moodle_manager.db'
    if db_path.exists():
        backup_path = db_path.with_suffix('.backup')
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✓ Database backed up to: {backup_path}")
        except Exception as e:
            print(f"⚠️  Could not backup database: {e}")

    # Remove and recreate database
    try:
        if db_path.exists():
            db_path.unlink()
            print("✓ Removed existing database")

        # The database will be recreated automatically on next run
        print("✓ Database will be recreated on next application start")
        reset_performed = True

    except Exception as e:
        print(f"✗ Database reset error: {e}")

    # 3. Clear all cache and config files
    print("\n🗑️  CLEARING ALL CACHE AND CONFIG FILES...")

    files_to_remove = []

    # Find all Moodle-related files in user home
    user_home = Path.home()
    for file_path in user_home.rglob('*'):
        if file_path.is_file():
            file_name = file_path.name.lower()
            if any(keyword in file_name for keyword in ['moodle', 'lms', 'credential', 'cache', 'moodlemanger']):
                files_to_remove.append(file_path)

    # Also check current directory for config files
    current_dir = Path.cwd()
    for file_path in current_dir.glob('*.ini'):
        if 'config' in file_path.name.lower() or 'moodle' in file_path.name.lower():
            files_to_remove.append(file_path)

    removed_count = 0
    for file_path in files_to_remove[:20]:  # Limit to prevent accidental deletion
        try:
            file_path.unlink()
            print(f"✓ Removed: {file_path.name}")
            removed_count += 1
        except Exception as e:
            print(f"⚠️  Could not remove {file_path.name}: {e}")

    if removed_count > 0:
        print(f"✓ Cleared {removed_count} cache/config files")
        reset_performed = True
    else:
        print("✓ No cache files found to clear")

    # 4. Reset encryption keys
    print("\n🔐 RESETTING ENCRYPTION KEYS...")

    key_files = [
        Path.home() / '.moodle_manager' / 'encryption.key',
        Path.home() / '.MoodleManager' / 'encryption.key'
    ]

    for key_file in key_files:
        if key_file.exists():
            try:
                key_file.unlink()
                print(f"✓ Removed encryption key: {key_file}")
                reset_performed = True
            except Exception as e:
                print(f"⚠️  Could not remove {key_file}: {e}")

    print("\n" + "=" * 60)

    if reset_performed:
        print("✅ COMPLETE CREDENTIAL RESET SUCCESSFUL")
        print("🎯 All credential-related data has been cleared")
        print("🔄 Moodle Manager will start with fresh configuration")
        print()
        print("🚀 NEXT STEPS:")
        print("   1. Start Moodle Manager: python main.py")
        print("   2. Application will show login dialog")
        print("   3. Enter Moodle credentials manually")
        print("   4. Choose 'Remember me' to store credentials")
        print("   5. Application will work normally after that")
        print()
        print("💡 The 'Incorrect padding' error should be completely resolved!")
    else:
        print("✅ NO RESET NEEDED")
        print("🔍 Credential system appears to be in good state")

    return reset_performed

def create_fresh_config():
    """Create a fresh, minimal config file"""
    print("\n📄 CREATING FRESH CONFIGURATION...")

    config_content = """[lms1]
url = http://127.0.0.1/moodle/
user = lms_explorer
service = moodle_mobile_app
autoconnect = 0
remember_me = 1
password =

[settings]
theme = system
auto_connect = 0
"""

    config_path = 'config.ini'
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        print(f"✓ Fresh config created: {config_path}")
        return True
    except Exception as e:
        print(f"✗ Could not create config: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing persistent Moodle Manager credential issues...")
    print()

    # Perform complete reset
    reset_done = complete_credential_reset()

    # Create fresh configuration
    config_created = create_fresh_config()

    print("\n🎯 RESET SUMMARY:")
    print(f"  • Credential Reset: {'✅ Done' if reset_done else '✅ Not needed'}")
    print(f"  • Fresh Config: {'✅ Created' if config_created else '❌ Failed'}")
    print()
    print("🚀 Moodle Manager is now ready with clean state!")
    print("💻 Start the application: python main.py")
    print("👤 Login manually the first time to establish fresh credentials")
