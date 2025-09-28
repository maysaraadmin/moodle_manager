"""
Utility functions for LMS Explorer
"""

import os
import sys
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def log_message(message: str, level: str = "INFO"):
    """Log a message with the specified level"""
    logger = logging.getLogger(__name__)
    log_level = getattr(logging, level.upper())
    logger.log(log_level, message)


def get_application_path() -> str:
    """Get the application path"""
    if getattr(sys, 'frozen', False):
        # Running as executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))


def get_config_path() -> str:
    """Get the configuration file path"""
    app_path = get_application_path()
    return os.path.join(app_path, 'config.ini')


def ensure_directory_exists(path: str) -> bool:
    """Ensure that a directory exists, create it if necessary"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid"""
    if not url:
        return False
    
    # Basic URL validation
    return url.startswith(('http://', 'https://'))


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_filename(filename: str) -> str:
    """Make filename safe for filesystem"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries"""
    result = dict1.copy()
    result.update(dict2)
    return result


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """Flatten a nested list"""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def find_in_list(lst: List[Any], key: str, value: Any) -> Optional[Any]:
    """Find an item in a list of dictionaries by key-value pair"""
    for item in lst:
        if isinstance(item, dict) and key in item and item[key] == value:
            return item
    return None


def remove_duplicates(lst: List[Any], key: Optional[str] = None) -> List[Any]:
    """Remove duplicates from a list"""
    if key is None:
        # Remove duplicates by value
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]
    else:
        # Remove duplicates by key
        seen = set()
        result = []
        for item in lst:
            if isinstance(item, dict) and key in item:
                if item[key] not in seen:
                    seen.add(item[key])
                    result.append(item)
            else:
                result.append(item)
        return result


def validate_email(email: str) -> bool:
    """Basic email validation"""
    if not email:
        return False
    
    # Basic email format check
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    local_part, domain = parts
    if not local_part or not domain:
        return False
    
    if '.' not in domain:
        return False
    
    return True


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    return get_file_extension(filename) in image_extensions


def is_document_file(filename: str) -> bool:
    """Check if file is a document"""
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'}
    return get_file_extension(filename) in doc_extensions


def create_backup_filename(original_path: str) -> str:
    """Create a backup filename with timestamp"""
    directory, filename = os.path.split(original_path)
    name, ext = os.path.splitext(filename)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{name}_backup_{timestamp}{ext}"
    
    return os.path.join(directory, backup_name)
