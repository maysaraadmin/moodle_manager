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