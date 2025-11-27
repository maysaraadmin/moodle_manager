#!/usr/bin/env python3
"""
System User Manager for Moodle Manager
Handles application-level user authentication and management
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import sqlite3
import json
import os
import hashlib
import base64
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class SystemUserManager:
    """System-level user management for the application"""

    def __init__(self, db_path: str = None):
        """Initialize system user manager"""
        if db_path is None:
            # Default database location
            app_data_dir = Path.home() / '.moodle_manager'
            app_data_dir.mkdir(exist_ok=True)
            db_path = app_data_dir / 'system_users.db'

        self.db_path = str(db_path)
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)

        # Initialize database
        self.init_database()

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = Path.home() / '.moodle_manager' / 'system_users.key'
        key_file.parent.mkdir(exist_ok=True)

        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return ""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return ""
        try:
            encrypted = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except:
            return ""

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def init_database(self):
        """Initialize system users database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('PRAGMA foreign_keys = ON')

            # System users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    is_admin BOOLEAN DEFAULT 0,
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # User sessions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES system_users(id) ON DELETE CASCADE
                )
            ''')

            # User preferences table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES system_users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, preference_key)
                )
            ''')

            # User activity log table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    activity_type TEXT NOT NULL,
                    activity_details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES system_users(id) ON DELETE SET NULL
                )
            ''')

            conn.commit()

    # User Management
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str = None, role: str = 'user', 
                   is_admin: bool = False) -> bool:
        """Create a new system user"""
        try:
            # Validate inputs
            if not username or not email or not password:
                return False
            
            # Check if user already exists
            if self.get_user_by_username(username) or self.get_user_by_email(email):
                return False

            hashed_password = self._hash_password(password)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO system_users 
                    (username, email, hashed_password, full_name, role, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, email, hashed_password, full_name, role, is_admin))
                conn.commit()
                
                # Log activity
                self.log_activity(cursor.lastrowid, 'user_created', 
                                f'User {username} created')
                return True

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        try:
            hashed_password = self._hash_password(password)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, username, email, full_name, role, is_active, is_admin, last_login
                    FROM system_users 
                    WHERE username = ? AND hashed_password = ? AND is_active = 1
                ''', (username, hashed_password))
                
                row = cursor.fetchone()
                if row:
                    # Update last login
                    conn.execute('''
                        UPDATE system_users 
                        SET last_login = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (row[0],))
                    conn.commit()

                    user_data = {
                        'id': row[0], 'username': row[1], 'email': row[2],
                        'full_name': row[3], 'role': row[4], 'is_active': bool(row[5]),
                        'is_admin': bool(row[6]), 'last_login': row[7]
                    }

                    # Log activity
                    self.log_activity(row[0], 'user_login', 'User logged in')
                    
                    return user_data
                return None

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, username, email, full_name, role, is_active, is_admin, 
                           last_login, created_at, updated_at
                    FROM system_users WHERE username = ?
                ''', (username,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0], 'username': row[1], 'email': row[2],
                        'full_name': row[3], 'role': row[4], 'is_active': bool(row[5]),
                        'is_admin': bool(row[6]), 'last_login': row[7],
                        'created_at': row[8], 'updated_at': row[9]
                    }
                return None

        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, username, email, full_name, role, is_active, is_admin,
                           last_login, created_at, updated_at
                    FROM system_users WHERE email = ?
                ''', (email,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0], 'username': row[1], 'email': row[2],
                        'full_name': row[3], 'role': row[4], 'is_active': bool(row[5]),
                        'is_admin': bool(row[6]), 'last_login': row[7],
                        'created_at': row[8], 'updated_at': row[9]
                    }
                return None

        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, username, email, full_name, role, is_active, is_admin,
                           last_login, created_at, updated_at
                    FROM system_users WHERE id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0], 'username': row[1], 'email': row[2],
                        'full_name': row[3], 'role': row[4], 'is_active': bool(row[5]),
                        'is_admin': bool(row[6]), 'last_login': row[7],
                        'created_at': row[8], 'updated_at': row[9]
                    }
                return None

        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    def update_user(self, user_id: int, **updates) -> bool:
        """Update user information"""
        try:
            allowed_fields = ['email', 'full_name', 'role', 'is_active', 'is_admin']
            update_fields = []
            update_values = []

            for field, value in updates.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)

            if not update_fields:
                return False

            update_values.append(user_id)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f'''
                    UPDATE system_users 
                    SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', update_values)
                conn.commit()

                # Log activity
                self.log_activity(user_id, 'user_updated', f'User updated: {", ".join(updates.keys())}')
                return True

        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        try:
            hashed_password = self._hash_password(new_password)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    UPDATE system_users 
                    SET hashed_password = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (hashed_password, user_id))
                conn.commit()

                if cursor.rowcount > 0:
                    # Log activity
                    self.log_activity(user_id, 'password_changed', 'Password changed')
                    return True
                return False

        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False

    def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by deactivating)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    UPDATE system_users 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (user_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    # Log activity
                    self.log_activity(user_id, 'user_deactivated', 'User deactivated')
                    return True
                return False

        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, username, email, full_name, role, is_active, is_admin,
                           last_login, created_at, updated_at
                    FROM system_users 
                    ORDER BY username
                ''')
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'id': row[0], 'username': row[1], 'email': row[2],
                        'full_name': row[3], 'role': row[4], 'is_active': bool(row[5]),
                        'is_admin': bool(row[6]), 'last_login': row[7],
                        'created_at': row[8], 'updated_at': row[9]
                    })
                return users

        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    # Session Management
    def create_session(self, user_id: int, ip_address: str = None, 
                      user_agent: str = None, expires_hours: int = 24) -> str:
        """Create user session"""
        try:
            import secrets
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=expires_hours)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO user_sessions 
                    (user_id, session_token, expires_at, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, session_token, expires_at, ip_address, user_agent))
                conn.commit()

                # Log activity
                self.log_activity(user_id, 'session_created', 'Session created')
                return session_token

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return ""

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT s.user_id, s.expires_at, u.username, u.email, u.full_name, 
                           u.role, u.is_admin
                    FROM user_sessions s
                    JOIN system_users u ON s.user_id = u.id
                    WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
                    AND u.is_active = 1
                ''', (session_token,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row[0], 'expires_at': row[1], 'username': row[2],
                        'email': row[3], 'full_name': row[4], 'role': row[5],
                        'is_admin': bool(row[6])
                    }
                return None

        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None

    def destroy_session(self, session_token: str) -> bool:
        """Destroy user session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get user_id before deleting for logging
                cursor = conn.execute('''
                    SELECT user_id FROM user_sessions WHERE session_token = ?
                ''', (session_token,))
                row = cursor.fetchone()
                
                cursor = conn.execute('''
                    DELETE FROM user_sessions WHERE session_token = ?
                ''', (session_token,))
                conn.commit()

                if cursor.rowcount > 0 and row:
                    # Log activity
                    self.log_activity(row[0], 'session_destroyed', 'Session destroyed')
                    return True
                return False

        except Exception as e:
            logger.error(f"Error destroying session: {e}")
            return False

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP
                ''')
                conn.commit()
                return cursor.rowcount

        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    # User Preferences
    def set_user_preference(self, user_id: int, key: str, value: Any) -> bool:
        """Set user preference"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, preference_key, preference_value, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, key, json.dumps(value) if isinstance(value, (dict, list)) else str(value)))
                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Error setting user preference: {e}")
            return False

    def get_user_preference(self, user_id: int, key: str, default: Any = None) -> Any:
        """Get user preference"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT preference_value FROM user_preferences 
                    WHERE user_id = ? AND preference_key = ?
                ''', (user_id, key))
                
                row = cursor.fetchone()
                if row:
                    try:
                        return json.loads(row[0])
                    except:
                        return row[0]
                return default

        except Exception as e:
            logger.error(f"Error getting user preference: {e}")
            return default

    def get_all_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get all user preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT preference_key, preference_value FROM user_preferences 
                    WHERE user_id = ?
                ''', (user_id,))
                
                preferences = {}
                for row in cursor.fetchall():
                    key, value = row
                    try:
                        preferences[key] = json.loads(value)
                    except:
                        preferences[key] = value
                return preferences

        except Exception as e:
            logger.error(f"Error getting all user preferences: {e}")
            return {}

    # Activity Logging
    def log_activity(self, user_id: int, activity_type: str, details: str = None,
                    ip_address: str = None):
        """Log user activity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO user_activity_log 
                    (user_id, activity_type, activity_details, ip_address)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, activity_type, details, ip_address))
                conn.commit()

        except Exception as e:
            logger.error(f"Error logging activity: {e}")

    def get_user_activity(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user activity log"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT activity_type, activity_details, ip_address, timestamp
                    FROM user_activity_log 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (user_id, limit))
                
                activities = []
                for row in cursor.fetchall():
                    activities.append({
                        'activity_type': row[0], 'activity_details': row[1],
                        'ip_address': row[2], 'timestamp': row[3]
                    })
                return activities

        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return []

    # Utility Methods
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # User counts
                cursor = conn.execute('SELECT COUNT(*) FROM system_users WHERE is_active = 1')
                stats['active_users'] = cursor.fetchone()[0]
                
                cursor = conn.execute('SELECT COUNT(*) FROM system_users')
                stats['total_users'] = cursor.fetchone()[0]
                
                # Session counts
                cursor = conn.execute('SELECT COUNT(*) FROM user_sessions WHERE expires_at > CURRENT_TIMESTAMP')
                stats['active_sessions'] = cursor.fetchone()[0]
                
                cursor = conn.execute('SELECT COUNT(*) FROM user_sessions')
                stats['total_sessions'] = cursor.fetchone()[0]
                
                return stats

        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}

    def close(self):
        """Close database connection"""
        pass
