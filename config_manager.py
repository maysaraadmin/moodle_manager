"""
Configuration Manager for LMS Explorer
Handles loading and saving configuration settings
"""

import os
import configparser
from typing import Dict, List, Optional
from credential_manager import get_credential_manager


class LMSConfig:
    """Configuration data for a single LMS instance"""
    
    def __init__(self, name: str = "", url: str = "", username: str = "", 
                 password: str = "", service: str = "moodle_mobile_app", 
                 autoconnect: bool = False, remember_me: bool = False):
        self.name = name
        self.url = url
        self.username = username
        self.password = password
        self.service = service
        self.autoconnect = autoconnect
        self.remember_me = remember_me
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for saving"""
        data = {
            'url': self.url,
            'user': self.username,
            'service': self.service,
            'autoconnect': '1' if self.autoconnect else '0',
            'remember_me': '1' if self.remember_me else '0'
        }
        
        # Never store password in config file - it's handled by credential manager
        data['password'] = ''
            
        return data
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, str]) -> 'LMSConfig':
        """Create from dictionary"""
        return cls(
            name=name,
            url=data.get('url', ''),
            username=data.get('user', ''),
            password=data.get('password', ''),
            service=data.get('service', 'moodle_mobile_app'),
            autoconnect=data.get('autoconnect', '0') == '1',
            remember_me=data.get('remember_me', '0') == '1'
        )


class ConfigManager:
    """Manages configuration settings for LMS Explorer"""
    
    def __init__(self):
        self.configs: Dict[str, LMSConfig] = {}
        self.config_file = ""
        self.credential_manager = get_credential_manager()
        
    def load_config(self, config_file: str):
        """Load configuration from file"""
        self.config_file = config_file
        
        if not os.path.exists(config_file):
            return
        
        config = configparser.ConfigParser()
        config.read(config_file)
        
        self.configs.clear()
        
        # Load each LMS configuration
        for section_name in config.sections():
            if section_name.startswith('lms'):
                lms_config = LMSConfig.from_dict(section_name, dict(config[section_name]))
                
                # If remember_me is enabled, retrieve password from credential manager
                if lms_config.remember_me:
                    service_name = f"lms_{lms_config.name}_{lms_config.url}"
                    credentials = self.credential_manager.get_credentials(service_name)
                    if credentials and credentials.get('remember', False):
                        lms_config.password = credentials.get('password', '')
                
                self.configs[section_name] = lms_config
    
    def save_config(self, config_file: str = None):
        """Save configuration to file"""
        if config_file is None:
            config_file = self.config_file
        
        if not config_file:
            return
        
        config = configparser.ConfigParser()
        
        # Save each LMS configuration
        for section_name, lms_config in self.configs.items():
            config[section_name] = lms_config.to_dict()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w') as f:
            config.write(f)
    
    def add_config(self, name: str, url: str, username: str, password: str, 
                   service: str = "moodle_mobile_app", autoconnect: bool = False, remember_me: bool = False):
        """Add a new LMS configuration"""
        section_name = f"lms{len(self.configs) + 1}"
        lms_config = LMSConfig(
            name=name,
            url=url,
            username=username,
            password=password,
            service=service,
            autoconnect=autoconnect,
            remember_me=remember_me
        )
        self.configs[section_name] = lms_config
        
        # Save credentials to credential manager if remember_me is enabled
        if remember_me:
            service_name = f"lms_{name}_{url}"
            self.credential_manager.save_credentials(
                service_name=service_name,
                username=username,
                password=password,
                remember=remember_me
            )
    
    def remove_config(self, section_name: str):
        """Remove an LMS configuration"""
        if section_name in self.configs:
            lms_config = self.configs[section_name]
            
            # Remove credentials from credential manager if they exist
            if lms_config.remember_me:
                service_name = f"lms_{lms_config.name}_{lms_config.url}"
                self.credential_manager.delete_credentials(service_name)
            
            del self.configs[section_name]
    
    def get_config(self, section_name: str) -> Optional[LMSConfig]:
        """Get a specific LMS configuration"""
        return self.configs.get(section_name)
    
    def get_all_configs(self) -> Dict[str, LMSConfig]:
        """Get all LMS configurations"""
        return self.configs.copy()
    
    def get_autoconnect_config(self) -> Optional[LMSConfig]:
        """Get the autoconnect configuration"""
        for config in self.configs.values():
            if config.autoconnect:
                return config
        return None
    
    def get_config_names(self) -> List[str]:
        """Get list of configuration names"""
        return list(self.configs.keys())
    
    def update_config(self, section_name: str, **kwargs):
        """Update an existing configuration"""
        if section_name in self.configs:
            config = self.configs[section_name]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
