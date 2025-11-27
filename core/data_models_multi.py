#!/usr/bin/env python3
"""
Multi-Platform Data Models for Moodle Manager
Handles multiple Moodle platform instances and their management
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class PlatformStatus(Enum):
    """Platform connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    AUTHENTICATING = "authenticating"


class AuthType(Enum):
    """Authentication types for Moodle platforms"""
    TOKEN = "token"
    USERNAME_PASSWORD = "username_password"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"


@dataclass
class PlatformCredentials:
    """Credentials for Moodle platform authentication"""
    auth_type: AuthType
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    additional_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


@dataclass
class MoodlePlatform:
    """Represents a Moodle platform instance"""
    id: str
    name: str
    url: str
    description: str
    credentials: PlatformCredentials
    status: PlatformStatus = PlatformStatus.DISCONNECTED
    created_at: datetime = None
    last_connected: Optional[datetime] = None
    connection_count: int = 0
    is_active: bool = True
    platform_version: Optional[str] = None
    site_name: Optional[str] = None
    admin_email: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    custom_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.custom_settings is None:
            self.custom_settings = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert platform to dictionary"""
        data = asdict(self)
        # Handle datetime serialization
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if data['last_connected']:
            data['last_connected'] = data['last_connected'].isoformat()
        # Handle enum serialization
        data['status'] = self.status.value
        data['credentials']['auth_type'] = self.credentials.auth_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoodlePlatform':
        """Create platform from dictionary"""
        # Handle datetime deserialization
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_connected'):
            data['last_connected'] = datetime.fromisoformat(data['last_connected'])
        
        # Handle enum deserialization
        data['status'] = PlatformStatus(data['status'])
        data['credentials'] = PlatformCredentials(
            auth_type=AuthType(data['credentials']['auth_type']),
            **{k: v for k, v in data['credentials'].items() if k != 'auth_type'}
        )
        
        return cls(**data)


@dataclass
class PlatformSession:
    """Represents an active session with a Moodle platform"""
    id: str
    platform_id: str
    session_token: str
    user_data: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    last_activity: Optional[datetime] = None
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()


class MultiPlatformManager:
    """Manages multiple Moodle platform instances"""
    
    def __init__(self):
        self.platforms: Dict[str, MoodlePlatform] = {}
        self.active_platform_id: Optional[str] = None
        self.sessions: Dict[str, PlatformSession] = {}
        self.config_file = os.path.join(project_root, "data", "multi_platform_config.json")
        self.load_config()
    
    def add_platform(self, platform: MoodlePlatform) -> str:
        """Add a new Moodle platform"""
        self.platforms[platform.id] = platform
        self.save_config()
        return platform.id
    
    def remove_platform(self, platform_id: str) -> bool:
        """Remove a Moodle platform"""
        if platform_id in self.platforms:
            # Remove associated sessions
            sessions_to_remove = [sid for sid, session in self.sessions.items() 
                                if session.platform_id == platform_id]
            for session_id in sessions_to_remove:
                del self.sessions[session_id]
            
            # Clear active platform if it was removed
            if self.active_platform_id == platform_id:
                self.active_platform_id = None
            
            del self.platforms[platform_id]
            self.save_config()
            return True
        return False
    
    def get_platform(self, platform_id: str) -> Optional[MoodlePlatform]:
        """Get a platform by ID"""
        return self.platforms.get(platform_id)
    
    def get_all_platforms(self) -> List[MoodlePlatform]:
        """Get all platforms"""
        return list(self.platforms.values())
    
    def get_active_platforms(self) -> List[MoodlePlatform]:
        """Get all active platforms"""
        return [p for p in self.platforms.values() if p.is_active]
    
    def set_active_platform(self, platform_id: str) -> bool:
        """Set the active platform"""
        if platform_id in self.platforms:
            self.active_platform_id = platform_id
            self.save_config()
            return True
        return False
    
    def get_active_platform(self) -> Optional[MoodlePlatform]:
        """Get the currently active platform"""
        if self.active_platform_id:
            return self.platforms.get(self.active_platform_id)
        return None
    
    def update_platform_status(self, platform_id: str, status: PlatformStatus):
        """Update platform connection status"""
        if platform_id in self.platforms:
            self.platforms[platform_id].status = status
            if status == PlatformStatus.CONNECTED:
                self.platforms[platform_id].last_connected = datetime.now()
                self.platforms[platform_id].connection_count += 1
            self.save_config()
    
    def create_session(self, platform_id: str, session_token: str, 
                      user_data: Dict[str, Any], expires_hours: int = 24) -> str:
        """Create a new session for a platform"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + datetime.timedelta(hours=expires_hours)
        
        session = PlatformSession(
            id=session_id,
            platform_id=platform_id,
            session_token=session_token,
            user_data=user_data,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        self.sessions[session_id] = session
        self.save_config()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[PlatformSession]:
        """Get a session by ID"""
        session = self.sessions.get(session_id)
        if session and session.is_active and not session.is_expired():
            return session
        return None
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.save_config()
            return True
        return False
    
    def get_platform_sessions(self, platform_id: str) -> List[PlatformSession]:
        """Get all sessions for a platform"""
        return [s for s in self.sessions.values() 
                if s.platform_id == platform_id and s.is_active and not s.is_expired()]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = [sid for sid, session in self.sessions.items() 
                           if session.is_expired()]
        for session_id in expired_sessions:
            del self.sessions[session_id]
        if expired_sessions:
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            config = {
                'platforms': {pid: platform.to_dict() for pid, platform in self.platforms.items()},
                'active_platform_id': self.active_platform_id,
                'sessions': {sid: {
                    'id': session.id,
                    'platform_id': session.platform_id,
                    'session_token': session.session_token,
                    'user_data': session.user_data,
                    'created_at': session.created_at.isoformat(),
                    'expires_at': session.expires_at.isoformat() if session.expires_at else None,
                    'is_active': session.is_active,
                    'last_activity': session.last_activity.isoformat() if session.last_activity else None
                } for sid, session in self.sessions.items()}
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving multi-platform config: {e}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Load platforms
                self.platforms = {}
                for platform_id, platform_data in config.get('platforms', {}).items():
                    self.platforms[platform_id] = MoodlePlatform.from_dict(platform_data)
                
                # Load active platform
                self.active_platform_id = config.get('active_platform_id')
                
                # Load sessions
                self.sessions = {}
                for session_id, session_data in config.get('sessions', {}).items():
                    session = PlatformSession(
                        id=session_data['id'],
                        platform_id=session_data['platform_id'],
                        session_token=session_data['session_token'],
                        user_data=session_data['user_data'],
                        created_at=datetime.fromisoformat(session_data['created_at']),
                        expires_at=datetime.fromisoformat(session_data['expires_at']) if session_data.get('expires_at') else None,
                        is_active=session_data['is_active'],
                        last_activity=datetime.fromisoformat(session_data['last_activity']) if session_data.get('last_activity') else None
                    )
                    self.sessions[session_id] = session
                
                # Cleanup expired sessions
                self.cleanup_expired_sessions()
                
        except Exception as e:
            print(f"Error loading multi-platform config: {e}")
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get statistics about platforms"""
        total_platforms = len(self.platforms)
        active_platforms = len(self.get_active_platforms())
        connected_platforms = len([p for p in self.platforms.values() if p.status == PlatformStatus.CONNECTED])
        total_sessions = len([s for s in self.sessions.values() if s.is_active and not s.is_expired()])
        
        return {
            'total_platforms': total_platforms,
            'active_platforms': active_platforms,
            'connected_platforms': connected_platforms,
            'total_sessions': total_sessions,
            'active_platform': self.get_active_platform().name if self.get_active_platform() else None
        }
    
    def export_platforms(self, file_path: str) -> bool:
        """Export platforms to file"""
        try:
            export_data = {
                'platforms': {pid: platform.to_dict() for pid, platform in self.platforms.items()},
                'exported_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting platforms: {e}")
            return False
    
    def import_platforms(self, file_path: str) -> int:
        """Import platforms from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for platform_id, platform_data in import_data.get('platforms', {}).items():
                # Generate new ID to avoid conflicts
                new_id = str(uuid.uuid4())
                platform_data['id'] = new_id
                platform = MoodlePlatform.from_dict(platform_data)
                self.platforms[new_id] = platform
                imported_count += 1
            
            if imported_count > 0:
                self.save_config()
            
            return imported_count
        except Exception as e:
            print(f"Error importing platforms: {e}")
            return 0
