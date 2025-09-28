"""
Utility functions for LMS Explorer
"""

import datetime
import re
from typing import Optional


class Utils:
    """Utility class for common functions"""
    
    # Global flag for hiding sensitive text
    _hide_sensitive = True
    
    @classmethod
    def set_hide_sensitive(cls, hide: bool):
        """Set whether to hide sensitive text"""
        cls._hide_sensitive = hide
    
    @classmethod
    def shadow_text(cls, text: str) -> str:
        """
        Create a shadow version of text by replacing some characters with asterisks
        Used for hiding sensitive information like passwords
        """
        if not cls._hide_sensitive:
            return text
        
        result = []
        for i, char in enumerate(text, 1):
            if (i % 3 == 0) or (i % 4 == 0):
                result.append('*')
            else:
                result.append(char)
        
        return ''.join(result)
    
    @staticmethod
    def format_datetime_never(dt: Optional[datetime.datetime]) -> str:
        """
        Format datetime, return 'Never' if datetime is invalid or None
        """
        if dt is None:
            return "Never"
        
        try:
            # Convert to timestamp to check if it's valid
            timestamp = dt.timestamp()
            if timestamp <= 0:
                return "Never"
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError, AttributeError):
            return "Never"
    
    @staticmethod
    def format_datetime_blank(dt: Optional[datetime.datetime]) -> str:
        """
        Format datetime, return empty string if datetime is invalid or None
        """
        if dt is None:
            return ""
        
        try:
            # Convert to timestamp to check if it's valid
            timestamp = dt.timestamp()
            if timestamp <= 0:
                return ""
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError, AttributeError):
            return ""
    
    @staticmethod
    def text_to_property_name(text: str) -> str:
        """
        Convert display text to property name
        e.g., "Full name" -> "Full_name"
        Replaces spaces with underscores
        """
        return text.replace(' ', '_')
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Simple email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to maximum length with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Convert filename to safe format by removing invalid characters"""
        # Remove or replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
