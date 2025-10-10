#!/usr/bin/env python3
"""
Moodle Manager Database System
Comprehensive database for storing all application data
"""

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


class DatabaseManager:
    """Main database manager for Moodle Manager"""

    def __init__(self, db_path: str = None):
        """Initialize database manager"""
        if db_path is None:
            # Default database location
            app_data_dir = Path.home() / '.moodle_manager'
            app_data_dir.mkdir(exist_ok=True)
            db_path = app_data_dir / 'moodle_manager.db'

        self.db_path = str(db_path)
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)

        # Initialize database
        self.init_database()

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = Path.home() / '.moodle_manager' / 'encryption.key'
        key_file.parent.mkdir(exist_ok=True)

        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set appropriate permissions on Unix systems
            try:
                key_file.chmod(0o600)
            except:
                pass  # Windows doesn't support chmod
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
            return ""  # Return empty if decryption fails

    def init_database(self):
        """Initialize database with all tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('PRAGMA foreign_keys = ON')

            # Application settings table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS app_settings (
                    id INTEGER PRIMARY KEY,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    setting_type TEXT DEFAULT 'string',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Moodle servers table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS moodle_servers (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER DEFAULT 8000,
                    service_name TEXT DEFAULT 'moodle_mobile_app',
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # FastAPI servers table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS fastapi_servers (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER DEFAULT 8000,
                    app_file TEXT DEFAULT 'main.py',
                    working_directory TEXT DEFAULT '.',
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    auto_start BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # User credentials table (encrypted)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_credentials (
                    id INTEGER PRIMARY KEY,
                    server_id INTEGER,
                    server_type TEXT NOT NULL, -- 'moodle' or 'fastapi'
                    username TEXT NOT NULL,
                    encrypted_password TEXT,
                    is_remembered BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES moodle_servers(id) ON DELETE CASCADE
                )
            ''')

            # Connection history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS connection_history (
                    id INTEGER PRIMARY KEY,
                    server_id INTEGER,
                    server_type TEXT NOT NULL,
                    connection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    response_time_ms INTEGER,
                    user_agent TEXT,
                    FOREIGN KEY (server_id) REFERENCES moodle_servers(id) ON DELETE CASCADE
                )
            ''')

            # API call history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS api_call_history (
                    id INTEGER PRIMARY KEY,
                    server_id INTEGER,
                    server_type TEXT NOT NULL,
                    api_function TEXT NOT NULL,
                    parameters TEXT, -- JSON string
                    response TEXT, -- JSON string (truncated if too large)
                    success BOOLEAN NOT NULL,
                    response_time_ms INTEGER,
                    error_message TEXT,
                    called_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES moodle_servers(id) ON DELETE CASCADE
                )
            ''')

            # Moodle data cache table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS moodle_data_cache (
                    id INTEGER PRIMARY KEY,
                    server_id INTEGER NOT NULL,
                    data_type TEXT NOT NULL, -- 'courses', 'users', 'categories', etc.
                    data_key TEXT NOT NULL, -- unique identifier for the data
                    data_value TEXT, -- JSON string
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES moodle_servers(id) ON DELETE CASCADE,
                    UNIQUE(server_id, data_type, data_key)
                )
            ''')

            # Application logs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS application_logs (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL, -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
                    module TEXT NOT NULL,
                    function TEXT,
                    message TEXT NOT NULL,
                    exception_details TEXT,
                    user_id INTEGER,
                    session_id TEXT
                )
            ''')

            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_moodle_servers_active ON moodle_servers(is_active)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_fastapi_servers_active ON fastapi_servers(is_active)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_credentials_server ON user_credentials(server_id, server_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_connection_history_time ON connection_history(connection_time)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_api_calls_time ON api_call_history(called_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_cache_expiry ON moodle_data_cache(expires_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON application_logs(timestamp)')

            conn.commit()

    # ==========================================
    # APPLICATION SETTINGS
    # ==========================================

    def save_setting(self, key: str, value: Any, setting_type: str = 'string') -> bool:
        """Save application setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO app_settings (setting_key, setting_value, setting_type, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, json.dumps(value) if setting_type == 'json' else str(value), setting_type))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving setting {key}: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get application setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT setting_value, setting_type FROM app_settings WHERE setting_key = ?', (key,))
                row = cursor.fetchone()
                if row:
                    value, setting_type = row
                    if setting_type == 'json':
                        return json.loads(value)
                    elif setting_type == 'int':
                        return int(value)
                    elif setting_type == 'bool':
                        return value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        return value
                return default
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return default

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all application settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT setting_key, setting_value, setting_type FROM app_settings')
                settings = {}
                for key, value, setting_type in cursor.fetchall():
                    if setting_type == 'json':
                        settings[key] = json.loads(value)
                    elif setting_type == 'int':
                        settings[key] = int(value)
                    elif setting_type == 'bool':
                        settings[key] = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        settings[key] = value
                return settings
        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            return {}

    # ==========================================
    # SERVER MANAGEMENT
    # ==========================================

    def save_moodle_server(self, name: str, host: str, port: int = 8000, service_name: str = 'moodle_mobile_app',
                          description: str = '', is_active: bool = True) -> int:
        """Save Moodle server configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT OR REPLACE INTO moodle_servers (name, host, port, service_name, description, is_active, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, host, port, service_name, description, is_active))
                conn.commit()
                return cursor.lastrowid or self.get_moodle_server_id(name)
        except Exception as e:
            logger.error(f"Error saving Moodle server {name}: {e}")
            return -1

    def get_moodle_server(self, name: str) -> Optional[Dict[str, Any]]:
        """Get Moodle server configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, name, host, port, service_name, description, is_active, created_at, updated_at
                    FROM moodle_servers WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'host': row[2],
                        'port': row[3],
                        'service_name': row[4],
                        'description': row[5],
                        'is_active': bool(row[6]),
                        'created_at': row[7],
                        'updated_at': row[8]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting Moodle server {name}: {e}")
            return None

    def get_moodle_server_id(self, name: str) -> int:
        """Get Moodle server ID by name"""
        server = self.get_moodle_server(name)
        return server['id'] if server else -1

    def get_all_moodle_servers(self) -> List[Dict[str, Any]]:
        """Get all Moodle servers"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, name, host, port, service_name, description, is_active, created_at, updated_at
                    FROM moodle_servers ORDER BY name
                ''')
                servers = []
                for row in cursor.fetchall():
                    servers.append({
                        'id': row[0],
                        'name': row[1],
                        'host': row[2],
                        'port': row[3],
                        'service_name': row[4],
                        'description': row[5],
                        'is_active': bool(row[6]),
                        'created_at': row[7],
                        'updated_at': row[8]
                    })
                return servers
        except Exception as e:
            logger.error(f"Error getting all Moodle servers: {e}")
            return []

    def delete_moodle_server(self, name: str) -> bool:
        """Delete Moodle server"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM moodle_servers WHERE name = ?', (name,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting Moodle server {name}: {e}")
            return False

    def save_fastapi_server(self, name: str, host: str, port: int = 8000, app_file: str = 'main.py',
                           working_directory: str = '.', description: str = '', auto_start: bool = False) -> int:
        """Save FastAPI server configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT OR REPLACE INTO fastapi_servers (name, host, port, app_file, working_directory, description, auto_start, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, host, port, app_file, working_directory, description, auto_start))
                conn.commit()
                return cursor.lastrowid or self.get_fastapi_server_id(name)
        except Exception as e:
            logger.error(f"Error saving FastAPI server {name}: {e}")
            return -1

    def get_fastapi_server(self, name: str) -> Optional[Dict[str, Any]]:
        """Get FastAPI server configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, name, host, port, app_file, working_directory, description, is_active, auto_start, created_at, updated_at
                    FROM fastapi_servers WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'host': row[2],
                        'port': row[3],
                        'app_file': row[4],
                        'working_directory': row[5],
                        'description': row[6],
                        'is_active': bool(row[7]),
                        'auto_start': bool(row[8]),
                        'created_at': row[9],
                        'updated_at': row[10]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting FastAPI server {name}: {e}")
            return None

    def get_fastapi_server_id(self, name: str) -> int:
        """Get FastAPI server ID by name"""
        server = self.get_fastapi_server(name)
        return server['id'] if server else -1

    def get_all_fastapi_servers(self) -> List[Dict[str, Any]]:
        """Get all FastAPI servers"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, name, host, port, app_file, working_directory, description, is_active, auto_start, created_at, updated_at
                    FROM fastapi_servers ORDER BY name
                ''')
                servers = []
                for row in cursor.fetchall():
                    servers.append({
                        'id': row[0],
                        'name': row[1],
                        'host': row[2],
                        'port': row[3],
                        'app_file': row[4],
                        'working_directory': row[5],
                        'description': row[6],
                        'is_active': bool(row[7]),
                        'auto_start': bool(row[8]),
                        'created_at': row[9],
                        'updated_at': row[10]
                    })
                return servers
        except Exception as e:
            logger.error(f"Error getting all FastAPI servers: {e}")
            return []

    # ==========================================
    # CREDENTIAL MANAGEMENT
    # ==========================================

    def save_credentials(self, server_id: int, server_type: str, username: str, password: str,
                        is_remembered: bool = False) -> bool:
        """Save user credentials (encrypted)"""
        try:
            encrypted_password = self._encrypt_data(password) if password else ""
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_credentials (server_id, server_type, username, encrypted_password, is_remembered, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (server_id, server_type, username, encrypted_password, is_remembered))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving credentials for server {server_id}: {e}")
            return False

    def get_credentials(self, server_id: int, server_type: str, username: str) -> Optional[Dict[str, Any]]:
        """Get user credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, username, encrypted_password, is_remembered, created_at, updated_at
                    FROM user_credentials WHERE server_id = ? AND server_type = ? AND username = ?
                ''', (server_id, server_type, username))
                row = cursor.fetchone()
                if row:
                    encrypted_password = row[2]
                    password = self._decrypt_data(encrypted_password) if encrypted_password else ""
                    return {
                        'id': row[0],
                        'username': row[1],
                        'password': password,
                        'is_remembered': bool(row[3]),
                        'created_at': row[4],
                        'updated_at': row[5]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting credentials for server {server_id}: {e}")
            return None

    def get_all_credentials_for_server(self, server_id: int, server_type: str) -> List[Dict[str, Any]]:
        """Get all credentials for a server"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, username, encrypted_password, is_remembered, created_at, updated_at
                    FROM user_credentials WHERE server_id = ? AND server_type = ?
                ''', (server_id, server_type))
                credentials = []
                for row in cursor.fetchall():
                    encrypted_password = row[2]
                    password = self._decrypt_data(encrypted_password) if encrypted_password else ""
                    credentials.append({
                        'id': row[0],
                        'username': row[1],
                        'password': password,
                        'is_remembered': bool(row[3]),
                        'created_at': row[4],
                        'updated_at': row[5]
                    })
                return credentials
        except Exception as e:
            logger.error(f"Error getting all credentials for server {server_id}: {e}")
            return []

    def delete_credentials(self, server_id: int, username: str) -> bool:
        """Delete user credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM user_credentials WHERE server_id = ? AND username = ?', (server_id, username))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting credentials for server {server_id}: {e}")
            return False

    # ==========================================
    # CONNECTION HISTORY
    # ==========================================

    def log_connection(self, server_id: int, server_type: str, success: bool,
                      error_message: str = None, response_time_ms: int = None, user_agent: str = None) -> bool:
        """Log connection attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO connection_history (server_id, server_type, success, error_message, response_time_ms, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (server_id, server_type, success, error_message, response_time_ms, user_agent))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging connection for server {server_id}: {e}")
            return False

    def get_connection_history(self, server_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get connection history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if server_id:
                    cursor = conn.execute('''
                        SELECT id, server_id, server_type, connection_time, success, error_message, response_time_ms, user_agent
                        FROM connection_history WHERE server_id = ? ORDER BY connection_time DESC LIMIT ?
                    ''', (server_id, limit))
                else:
                    cursor = conn.execute('''
                        SELECT id, server_id, server_type, connection_time, success, error_message, response_time_ms, user_agent
                        FROM connection_history ORDER BY connection_time DESC LIMIT ?
                    ''', (limit,))

                history = []
                for row in cursor.fetchall():
                    history.append({
                        'id': row[0],
                        'server_id': row[1],
                        'server_type': row[2],
                        'connection_time': row[3],
                        'success': bool(row[4]),
                        'error_message': row[5],
                        'response_time_ms': row[6],
                        'user_agent': row[7]
                    })
                return history
        except Exception as e:
            logger.error(f"Error getting connection history: {e}")
            return []

    # ==========================================
    # API CALL HISTORY
    # ==========================================

    def log_api_call(self, server_id: int, server_type: str, api_function: str, parameters: Dict,
                    response: Any, success: bool, response_time_ms: int = None, error_message: str = None) -> bool:
        """Log API call"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Truncate response if too large
                response_str = json.dumps(response) if response else ""
                if len(response_str) > 5000:  # Limit response size
                    response_str = response_str[:5000] + "... [truncated]"

                conn.execute('''
                    INSERT INTO api_call_history (server_id, server_type, api_function, parameters, response, success, response_time_ms, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (server_id, server_type, api_function, json.dumps(parameters), response_str, success, response_time_ms, error_message))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging API call for server {server_id}: {e}")
            return False

    def get_api_call_history(self, server_id: int = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get API call history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if server_id:
                    cursor = conn.execute('''
                        SELECT id, server_id, server_type, api_function, parameters, response, success, response_time_ms, error_message, called_at
                        FROM api_call_history WHERE server_id = ? ORDER BY called_at DESC LIMIT ?
                    ''', (server_id, limit))
                else:
                    cursor = conn.execute('''
                        SELECT id, server_id, server_type, api_function, parameters, response, success, response_time_ms, error_message, called_at
                        FROM api_call_history ORDER BY called_at DESC LIMIT ?
                    ''', (limit,))

                history = []
                for row in cursor.fetchall():
                    history.append({
                        'id': row[0],
                        'server_id': row[1],
                        'server_type': row[2],
                        'api_function': row[3],
                        'parameters': json.loads(row[4]) if row[4] else {},
                        'response': row[5],
                        'success': bool(row[6]),
                        'response_time_ms': row[7],
                        'error_message': row[8],
                        'called_at': row[9]
                    })
                return history
        except Exception as e:
            logger.error(f"Error getting API call history: {e}")
            return []

    # ==========================================
    # DATA CACHE
    # ==========================================

    def cache_data(self, server_id: int, data_type: str, data_key: str, data_value: Any,
                   expiry_hours: int = 24) -> bool:
        """Cache Moodle data"""
        try:
            expires_at = datetime.now() + timedelta(hours=expiry_hours)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO moodle_data_cache (server_id, data_type, data_key, data_value, expires_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (server_id, data_type, data_key, json.dumps(data_value), expires_at))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error caching data for server {server_id}: {e}")
            return False

    def get_cached_data(self, server_id: int, data_type: str, data_key: str) -> Any:
        """Get cached Moodle data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT data_value, expires_at FROM moodle_data_cache
                    WHERE server_id = ? AND data_type = ? AND data_key = ? AND expires_at > CURRENT_TIMESTAMP
                ''', (server_id, data_type, data_key))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
        except Exception as e:
            logger.error(f"Error getting cached data for server {server_id}: {e}")
            return None

    def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('DELETE FROM moodle_data_cache WHERE expires_at <= CURRENT_TIMESTAMP')
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0

    # ==========================================
    # APPLICATION LOGS
    # ==========================================

    def log_message(self, level: str, module: str, function: str, message: str,
                   exception_details: str = None, user_id: int = None, session_id: str = None) -> bool:
        """Log application message"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO application_logs (level, module, function, message, exception_details, user_id, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (level, module, function, message, exception_details, user_id, session_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging message: {e}")
            return False

    def get_logs(self, level: str = None, module: str = None, limit: int = 100,
                since: datetime = None) -> List[Dict[str, Any]]:
        """Get application logs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = 'SELECT id, timestamp, level, module, function, message, exception_details, user_id, session_id FROM application_logs'
                params = []

                conditions = []
                if level:
                    conditions.append('level = ?')
                    params.append(level)
                if module:
                    conditions.append('module = ?')
                    params.append(module)
                if since:
                    conditions.append('timestamp >= ?')
                    params.append(since)

                if conditions:
                    query += ' WHERE ' + ' AND '.join(conditions)

                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)

                cursor = conn.execute(query, params)
                logs = []
                for row in cursor.fetchall():
                    logs.append({
                        'id': row[0],
                        'timestamp': row[1],
                        'level': row[2],
                        'module': row[3],
                        'function': row[4],
                        'message': row[5],
                        'exception_details': row[6],
                        'user_id': row[7],
                        'session_id': row[8]
                    })
                return logs
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []

    # ==========================================
    # UTILITY METHODS
    # ==========================================

    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Clean up old data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            with sqlite3.connect(self.db_path) as conn:
                # Delete old connection history
                cursor = conn.execute('DELETE FROM connection_history WHERE connection_time < ?', (cutoff_date,))
                connection_deleted = cursor.rowcount

                # Delete old API call history
                cursor = conn.execute('DELETE FROM api_call_history WHERE called_at < ?', (cutoff_date,))
                api_deleted = cursor.rowcount

                # Delete old logs
                cursor = conn.execute('DELETE FROM application_logs WHERE timestamp < ?', (cutoff_date,))
                logs_deleted = cursor.rowcount

                conn.commit()

                return {
                    'connection_history': connection_deleted,
                    'api_calls': api_deleted,
                    'application_logs': logs_deleted
                }
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return {}

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}

                # Table counts
                tables = ['moodle_servers', 'fastapi_servers', 'user_credentials', 'connection_history',
                         'api_call_history', 'moodle_data_cache', 'application_logs']

                for table in tables:
                    cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
                    stats[table] = cursor.fetchone()[0]

                # Database size
                db_size = os.path.getsize(self.db_path)
                stats['database_size_bytes'] = db_size
                stats['database_size_mb'] = db_size / (1024 * 1024)

                return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return False

    def vacuum_database(self) -> bool:
        """Optimize database by running VACUUM"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('VACUUM')
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error vacuuming database: {e}")
            return False

    def close(self):
        """Close database connection"""
        # SQLite connections are closed automatically
        pass
