#!/usr/bin/env python3
"""
Moodle Manager - Unified Database System
Consolidated database manager combining the best features of both implementations
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


class DatabaseManager:
    """Unified database manager for Moodle Manager"""

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
        # Store encryption key in database instead of file (more secure)
        key_data = self._get_db_setting('encryption_key')
        if key_data:
            return key_data.encode()

        # Generate new key and store in database
        key = Fernet.generate_key()
        self._set_db_setting('encryption_key', key.decode())
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

    def _set_db_setting(self, key: str, value: Any) -> bool:
        """Set a database setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO db_settings (setting_key, setting_value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, json.dumps(value) if isinstance(value, (dict, list)) else str(value)))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error setting DB setting {key}: {e}")
            return False

    def _get_db_setting(self, key: str, default: Any = None) -> Any:
        """Get a database setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT setting_value FROM db_settings WHERE setting_key = ?', (key,))
                row = cursor.fetchone()
                if row:
                    value = row[0]
                    try:
                        return json.loads(value)
                    except:
                        return value
                return default
        except Exception as e:
            logger.error(f"Error getting DB setting {key}: {e}")
            return default

    def init_database(self):
        """Initialize database with all tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('PRAGMA foreign_keys = ON')

            # Database settings table (for internal use)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS db_settings (
                    id INTEGER PRIMARY KEY,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

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
                    username TEXT,
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
                    parameters TEXT,
                    response_time_ms INTEGER,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    call_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_agent TEXT,
                    FOREIGN KEY (server_id) REFERENCES moodle_servers(id) ON DELETE CASCADE
                )
            ''')

            # Data cache table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS data_cache (
                    id INTEGER PRIMARY KEY,
                    server_id INTEGER,
                    server_type TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    data_key TEXT NOT NULL,
                    data_value TEXT,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_id) REFERENCES moodle_servers(id) ON DELETE CASCADE,
                    UNIQUE(server_id, data_type, data_key)
                )
            ''')

            # Application logs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS app_logs (
                    id INTEGER PRIMARY KEY,
                    level TEXT NOT NULL,
                    module TEXT NOT NULL,
                    function TEXT,
                    message TEXT NOT NULL,
                    details TEXT,
                    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    session_id TEXT
                )
            ''')

            conn.commit()

    # Settings Management
    def save_setting(self, key: str, value: Any, setting_type: str = 'string') -> bool:
        """Save application setting"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO app_settings (setting_key, setting_value, setting_type, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, json.dumps(value) if isinstance(value, (dict, list)) else str(value), setting_type))
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
                    if setting_type in ['json', 'dict', 'list']:
                        try:
                            return json.loads(value)
                        except:
                            return value
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
                for row in cursor.fetchall():
                    key, value, setting_type = row
                    if setting_type in ['json', 'dict', 'list']:
                        try:
                            settings[key] = json.loads(value)
                        except:
                            settings[key] = value
                    else:
                        settings[key] = value
                return settings
        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            return {}

    # Moodle Server Management
    def save_moodle_server(self, name: str, host: str, port: int = 8000, service_name: str = 'moodle_mobile_app',
                          description: str = None) -> int:
        """Save Moodle server configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT OR REPLACE INTO moodle_servers (name, host, port, service_name, description, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, host, port, service_name, description))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving Moodle server {name}: {e}")
            return 0

    def get_moodle_server(self, name: str) -> Optional[Dict[str, Any]]:
        """Get Moodle server by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, name, host, port, service_name, description, is_active, created_at, updated_at
                    FROM moodle_servers WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0], 'name': row[1], 'host': row[2], 'port': row[3],
                        'service_name': row[4], 'description': row[5], 'is_active': bool(row[6]),
                        'created_at': row[7], 'updated_at': row[8]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting Moodle server {name}: {e}")
            return None

    def get_moodle_server_id(self, name: str) -> int:
        """Get Moodle server ID by name"""
        server = self.get_moodle_server(name)
        return server['id'] if server else 0

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
                        'id': row[0], 'name': row[1], 'host': row[2], 'port': row[3],
                        'service_name': row[4], 'description': row[5], 'is_active': bool(row[6]),
                        'created_at': row[7], 'updated_at': row[8]
                    })
                return servers
        except Exception as e:
            logger.error(f"Error getting all Moodle servers: {e}")
            return []

    def delete_moodle_server(self, name: str) -> bool:
        """Delete Moodle server"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('DELETE FROM moodle_servers WHERE name = ?', (name,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting Moodle server {name}: {e}")
            return False

    # FastAPI Server Management
    def save_fastapi_server(self, name: str, host: str, port: int = 8000, app_file: str = 'main.py',
                           working_directory: str = '.', description: str = None) -> int:
        """Save FastAPI server configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT OR REPLACE INTO fastapi_servers 
                    (name, host, port, app_file, working_directory, description, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, host, port, app_file, working_directory, description))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving FastAPI server {name}: {e}")
            return 0

    def get_fastapi_server(self, name: str) -> Optional[Dict[str, Any]]:
        """Get FastAPI server by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, name, host, port, app_file, working_directory, description, 
                           is_active, auto_start, created_at, updated_at
                    FROM fastapi_servers WHERE name = ?
                ''', (name,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0], 'name': row[1], 'host': row[2], 'port': row[3],
                        'app_file': row[4], 'working_directory': row[5], 'description': row[6],
                        'is_active': bool(row[7]), 'auto_start': bool(row[8]),
                        'created_at': row[9], 'updated_at': row[10]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting FastAPI server {name}: {e}")
            return None

    def get_fastapi_server_id(self, name: str) -> int:
        """Get FastAPI server ID by name"""
        server = self.get_fastapi_server(name)
        return server['id'] if server else 0

    def get_all_fastapi_servers(self) -> List[Dict[str, Any]]:
        """Get all FastAPI servers"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, name, host, port, app_file, working_directory, description,
                           is_active, auto_start, created_at, updated_at
                    FROM fastapi_servers ORDER BY name
                ''')
                servers = []
                for row in cursor.fetchall():
                    servers.append({
                        'id': row[0], 'name': row[1], 'host': row[2], 'port': row[3],
                        'app_file': row[4], 'working_directory': row[5], 'description': row[6],
                        'is_active': bool(row[7]), 'auto_start': bool(row[8]),
                        'created_at': row[9], 'updated_at': row[10]
                    })
                return servers
        except Exception as e:
            logger.error(f"Error getting all FastAPI servers: {e}")
            return []

    # Credentials Management
    def save_credentials(self, server_id: int, server_type: str, username: str, password: str,
                        is_remembered: bool = False) -> bool:
        """Save user credentials (encrypted)"""
        try:
            encrypted_password = self._encrypt_data(password)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_credentials 
                    (server_id, server_type, username, encrypted_password, is_remembered, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (server_id, server_type, username, encrypted_password, is_remembered))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            return False

    def get_credentials(self, server_id: int, server_type: str, username: str) -> Optional[Dict[str, Any]]:
        """Get user credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, username, encrypted_password, is_remembered, created_at, updated_at
                    FROM user_credentials 
                    WHERE server_id = ? AND server_type = ? AND username = ?
                ''', (server_id, server_type, username))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0], 'username': row[1],
                        'password': self._decrypt_data(row[2]),
                        'is_remembered': bool(row[3]),
                        'created_at': row[4], 'updated_at': row[5]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            return None

    def get_all_credentials_for_server(self, server_id: int, server_type: str) -> List[Dict[str, Any]]:
        """Get all credentials for a server"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, username, encrypted_password, is_remembered, created_at, updated_at
                    FROM user_credentials 
                    WHERE server_id = ? AND server_type = ?
                ''', (server_id, server_type))
                credentials = []
                for row in cursor.fetchall():
                    credentials.append({
                        'id': row[0], 'username': row[1],
                        'password': self._decrypt_data(row[2]),
                        'is_remembered': bool(row[3]),
                        'created_at': row[4], 'updated_at': row[5]
                    })
                return credentials
        except Exception as e:
            logger.error(f"Error getting all credentials for server: {e}")
            return []

    def delete_credentials(self, server_id: int, username: str) -> bool:
        """Delete user credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM user_credentials WHERE server_id = ? AND username = ?
                ''', (server_id, username))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting credentials: {e}")
            return False

    def clear_all_credentials(self) -> bool:
        """Clear all stored credentials"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('DELETE FROM user_credentials')
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error clearing all credentials: {e}")
            return False

    # Connection History
    def log_connection(self, server_id: int, server_type: str, success: bool,
                      username: str = None, error_message: str = None,
                      response_time_ms: int = None, user_agent: str = None) -> bool:
        """Log connection attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO connection_history 
                    (server_id, server_type, username, success, error_message, 
                     response_time_ms, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (server_id, server_type, username, success, error_message,
                      response_time_ms, user_agent))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging connection: {e}")
            return False

    def get_connection_history(self, server_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get connection history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if server_id:
                    cursor = conn.execute('''
                        SELECT id, server_id, server_type, username, connection_time, success,
                               error_message, response_time_ms, user_agent
                        FROM connection_history 
                        WHERE server_id = ?
                        ORDER BY connection_time DESC LIMIT ?
                    ''', (server_id, limit))
                else:
                    cursor = conn.execute('''
                        SELECT id, server_id, server_type, username, connection_time, success,
                               error_message, response_time_ms, user_agent
                        FROM connection_history 
                        ORDER BY connection_time DESC LIMIT ?
                    ''', (limit,))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'id': row[0], 'server_id': row[1], 'server_type': row[2],
                        'username': row[3], 'connection_time': row[4],
                        'success': bool(row[5]), 'error_message': row[6],
                        'response_time_ms': row[7], 'user_agent': row[8]
                    })
                return history
        except Exception as e:
            logger.error(f"Error getting connection history: {e}")
            return []

    # Data Cache Management
    def cache_data(self, server_id: int, data_type: str, data_key: str, data_value: Any,
                   expires_in_hours: int = 1) -> bool:
        """Cache data with expiration"""
        try:
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            serialized_value = json.dumps(data_value) if not isinstance(data_value, str) else data_value
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO data_cache 
                    (server_id, data_type, data_key, data_value, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (server_id, data_type, data_key, serialized_value, expires_at))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            return False

    def get_cached_data(self, server_id: int, data_type: str, data_key: str) -> Any:
        """Get cached data if not expired"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT data_value, expires_at FROM data_cache 
                    WHERE server_id = ? AND data_type = ? AND data_key = ?
                ''', (server_id, data_type, data_key))
                row = cursor.fetchone()
                if row:
                    data_value, expires_at = row
                    if expires_at and datetime.fromisoformat(expires_at) > datetime.now():
                        try:
                            return json.loads(data_value)
                        except:
                            return data_value
                    else:
                        # Remove expired cache entry
                        conn.execute('''
                            DELETE FROM data_cache 
                            WHERE server_id = ? AND data_type = ? AND data_key = ?
                        ''', (server_id, data_type, data_key))
                        conn.commit()
                return None
        except Exception as e:
            logger.error(f"Error getting cached data: {e}")
            return None

    def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM data_cache WHERE expires_at < CURRENT_TIMESTAMP
                ''')
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0

    # Logging
    def log_message(self, level: str, module: str, function: str, message: str,
                   details: str = None, user_id: int = None, session_id: str = None) -> bool:
        """Log application message"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO app_logs (level, module, function, message, details, user_id, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (level, module, function, message, details, user_id, session_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging message: {e}")
            return False

    def get_logs(self, level: str = None, module: str = None, limit: int = 100,
                start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        """Get application logs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT id, level, module, function, message, details, log_time, user_id, session_id
                    FROM app_logs WHERE 1=1
                '''
                params = []
                
                if level:
                    query += ' AND level = ?'
                    params.append(level)
                if module:
                    query += ' AND module = ?'
                    params.append(module)
                if start_time:
                    query += ' AND log_time >= ?'
                    params.append(start_time)
                if end_time:
                    query += ' AND log_time <= ?'
                    params.append(end_time)
                    
                query += ' ORDER BY log_time DESC LIMIT ?'
                params.append(limit)
                
                cursor = conn.execute(query, params)
                logs = []
                for row in cursor.fetchall():
                    logs.append({
                        'id': row[0], 'level': row[1], 'module': row[2], 'function': row[3],
                        'message': row[4], 'details': row[5], 'log_time': row[6],
                        'user_id': row[7], 'session_id': row[8]
                    })
                return logs
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []

    # Maintenance
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Clean up old data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            results = {}
            
            with sqlite3.connect(self.db_path) as conn:
                # Clean old connection history
                cursor = conn.execute('''
                    DELETE FROM connection_history WHERE connection_time < ?
                ''', (cutoff_date,))
                results['connection_history'] = cursor.rowcount
                
                # Clean old API call history
                cursor = conn.execute('''
                    DELETE FROM api_call_history WHERE call_time < ?
                ''', (cutoff_date,))
                results['api_call_history'] = cursor.rowcount
                
                # Clean old logs
                cursor = conn.execute('''
                    DELETE FROM app_logs WHERE log_time < ?
                ''', (cutoff_date,))
                results['app_logs'] = cursor.rowcount
                
                # Clean expired cache
                results['expired_cache'] = self.clear_expired_cache()
                
                conn.commit()
                
            return results
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return {}

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Get table row counts
                tables = ['moodle_servers', 'fastapi_servers', 'user_credentials',
                          'connection_history', 'api_call_history', 'data_cache', 'app_logs']
                
                for table in tables:
                    cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
                    stats[f'{table}_count'] = cursor.fetchone()[0]
                
                # Get database size
                cursor = conn.execute('SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()')
                stats['database_size_bytes'] = cursor.fetchone()[0]
                
                return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

    def backup_database(self, backup_path: str) -> bool:
        """Backup database to specified path"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False

    def vacuum_database(self) -> bool:
        """Optimize database"""
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
        # SQLite connections are automatically closed when using 'with' statement
        pass
