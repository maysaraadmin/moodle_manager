#!/usr/bin/env python3
"""
Database Migration System for Moodle Manager
Handles database schema updates and data migrations
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Database migration system"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations_table = 'database_migrations'

    def init_migrations_table(self):
        """Initialize migrations tracking table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    id INTEGER PRIMARY KEY,
                    migration_name TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            ''')
            conn.commit()

    def get_applied_migrations(self) -> set:
        """Get list of applied migrations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(f'SELECT migration_name FROM {self.migrations_table} WHERE success = 1')
                return {row[0] for row in cursor.fetchall()}
        except:
            return set()

    def mark_migration_applied(self, migration_name: str, success: bool = True, error_message: str = None):
        """Mark migration as applied"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(f'''
                    INSERT INTO {self.migrations_table} (migration_name, success, error_message)
                    VALUES (?, ?, ?)
                ''', (migration_name, success, error_message))
                conn.commit()
        except Exception as e:
            logger.error(f"Error marking migration {migration_name}: {e}")

    def run_migrations(self) -> bool:
        """Run all pending migrations"""
        self.init_migrations_table()

        applied_migrations = self.get_applied_migrations()
        migrations_dir = Path(__file__).parent / 'migrations'

        if not migrations_dir.exists():
            migrations_dir.mkdir()
            return True

        success = True

        # Get all migration files
        migration_files = sorted(migrations_dir.glob('*.sql'))

        for migration_file in migration_files:
            migration_name = migration_file.stem

            if migration_name not in applied_migrations:
                logger.info(f"Running migration: {migration_name}")
                if self.run_migration(migration_file, migration_name):
                    logger.info(f"Migration {migration_name} completed successfully")
                else:
                    logger.error(f"Migration {migration_name} failed")
                    success = False

        return success

    def run_migration(self, migration_file: Path, migration_name: str) -> bool:
        """Run a single migration"""
        try:
            with open(migration_file, 'r') as f:
                sql_content = f.read()

            with sqlite3.connect(self.db_path) as conn:
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

                for statement in statements:
                    if statement:
                        conn.execute(statement)

                conn.commit()

            self.mark_migration_applied(migration_name, True)
            return True

        except Exception as e:
            error_msg = f"Migration {migration_name} failed: {str(e)}"
            logger.error(error_msg)
            self.mark_migration_applied(migration_name, False, error_msg)
            return False


def create_initial_migration():
    """Create initial database migration file"""
    migrations_dir = Path(__file__).parent / 'migrations'
    migrations_dir.mkdir(exist_ok=True)

    migration_content = '''
    -- Initial database schema for Moodle Manager
    -- This migration creates all base tables

    -- Application settings table
    CREATE TABLE IF NOT EXISTS app_settings (
        id INTEGER PRIMARY KEY,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT,
        setting_type TEXT DEFAULT 'string',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Moodle servers table
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
    );

    -- FastAPI servers table
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
    );

    -- User credentials table (encrypted)
    CREATE TABLE IF NOT EXISTS user_credentials (
        id INTEGER PRIMARY KEY,
        server_id INTEGER,
        server_type TEXT NOT NULL,
        username TEXT NOT NULL,
        encrypted_password TEXT,
        is_remembered BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (server_id) REFERENCES moodle_servers(id) ON DELETE CASCADE
    );

    -- Connection history table
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
    );

    -- API call history table
    CREATE TABLE IF NOT EXISTS api_call_history (
        id INTEGER PRIMARY KEY,
        server_id INTEGER,
        server_type TEXT NOT NULL,
        api_function TEXT NOT NULL,
        parameters TEXT,
        response TEXT,
        success BOOLEAN NOT NULL,
        response_time_ms INTEGER,
        error_message TEXT,
        called_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (server_id) REFERENCES moodle_servers(id) ON DELETE CASCADE
    );

    -- Moodle data cache table
    CREATE TABLE IF NOT EXISTS moodle_data_cache (
        id INTEGER PRIMARY KEY,
        server_id INTEGER NOT NULL,
        data_type TEXT NOT NULL,
        data_key TEXT NOT NULL,
        data_value TEXT,
        expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (server_id) REFERENCES moodle_servers(id) ON DELETE CASCADE,
        UNIQUE(server_id, data_type, data_key)
    );

    -- Application logs table
    CREATE TABLE IF NOT EXISTS application_logs (
        id INTEGER PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        level TEXT NOT NULL,
        module TEXT NOT NULL,
        function TEXT,
        message TEXT NOT NULL,
        exception_details TEXT,
        user_id INTEGER,
        session_id TEXT
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_moodle_servers_active ON moodle_servers(is_active);
    CREATE INDEX IF NOT EXISTS idx_fastapi_servers_active ON fastapi_servers(is_active);
    CREATE INDEX IF NOT EXISTS idx_credentials_server ON user_credentials(server_id, server_type);
    CREATE INDEX IF NOT EXISTS idx_connection_history_time ON connection_history(connection_time);
    CREATE INDEX IF NOT EXISTS idx_api_calls_time ON api_call_history(called_at);
    CREATE INDEX IF NOT EXISTS idx_cache_expiry ON moodle_data_cache(expires_at);
    CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON application_logs(timestamp);
    '''

    migration_file = migrations_dir / '001_initial_schema.sql'
    with open(migration_file, 'w') as f:
        f.write(migration_content.strip())

    print(f"Created initial migration: {migration_file}")


def create_migrations_directory():
    """Create migrations directory structure"""
    migrations_dir = Path(__file__).parent / 'migrations'
    migrations_dir.mkdir(exist_ok=True)

    # Create __init__.py
    init_file = migrations_dir / '__init__.py'
    if not init_file.exists():
        with open(init_file, 'w') as f:
            f.write('')

    print(f"Migrations directory created: {migrations_dir}")


if __name__ == "__main__":
    print("Setting up Moodle Manager database migrations...")

    # Create migrations directory
    create_migrations_directory()

    # Create initial migration
    create_initial_migration()

    print("Database migration system initialized successfully!")
