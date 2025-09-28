"""
Images helper for LMS Explorer
Handles image loading and management
"""

import os
import sys
from typing import Dict, Optional, Tuple
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication


class ImageHelper:
    """Helper class for managing application images and icons"""
    
    def __init__(self):
        self._icon_cache: Dict[str, QIcon] = {}
        self._pixmap_cache: Dict[str, QPixmap] = {}
        self._resource_paths = []
        
        # Initialize default resource paths
        self._init_resource_paths()
    
    def _init_resource_paths(self):
        """Initialize default resource paths"""
        # Get application directory
        if hasattr(QApplication, 'applicationDirPath'):
            app_dir = QApplication.applicationDirPath()
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Add resource directories
        resource_dirs = [
            os.path.join(app_dir, '..', '..', 'resources'),  # Project resources
            os.path.join(app_dir, 'resources'),  # Local resources
            os.path.join(app_dir, 'icons'),  # Local icons
        ]
        
        for resource_dir in resource_dirs:
            if os.path.exists(resource_dir):
                self._resource_paths.append(resource_dir)
    
    def add_resource_path(self, path: str):
        """
        Add a resource path to search for images
        Args:
            path: Directory path containing images
        """
        if os.path.exists(path) and path not in self._resource_paths:
            self._resource_paths.append(path)
    
    def find_image_file(self, image_name: str) -> Optional[str]:
        """
        Find an image file by name in resource paths
        Args:
            image_name: Name of the image file (with or without extension)
        Returns:
            Full path to the image file or None if not found
        """
        # Check if image_name already has a path
        if os.path.isabs(image_name) and os.path.exists(image_name):
            return image_name
        
        # Try different extensions
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.ico', '.svg']
        
        # If image_name already has an extension, try it first
        if any(image_name.lower().endswith(ext) for ext in extensions):
            for resource_path in self._resource_paths:
                full_path = os.path.join(resource_path, image_name)
                if os.path.exists(full_path):
                    return full_path
        
        # Try adding extensions
        for ext in extensions:
            for resource_path in self._resource_paths:
                # Try with extension
                full_path = os.path.join(resource_path, image_name + ext)
                if os.path.exists(full_path):
                    return full_path
                
                # Try replacing existing extension
                base_name = os.path.splitext(image_name)[0]
                full_path = os.path.join(resource_path, base_name + ext)
                if os.path.exists(full_path):
                    return full_path
        
        return None
    
    def get_icon(self, image_name: str, size: Optional[QSize] = None) -> QIcon:
        """
        Get an icon by name
        Args:
            image_name: Name of the icon file
            size: Optional size for the icon
        Returns:
            QIcon object
        """
        cache_key = f"{image_name}_{size.width() if size else 0}x{size.height() if size else 0}"
        
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        
        # Find image file
        image_path = self.find_image_file(image_name)
        if not image_path:
            # Return empty icon if not found
            icon = QIcon()
            self._icon_cache[cache_key] = icon
            return icon
        
        # Load icon
        icon = QIcon(image_path)
        
        # Scale if size is specified
        if size:
            pixmap = icon.pixmap(size)
            icon = QIcon(pixmap)
        
        self._icon_cache[cache_key] = icon
        return icon
    
    def get_pixmap(self, image_name: str, size: Optional[QSize] = None) -> QPixmap:
        """
        Get a pixmap by name
        Args:
            image_name: Name of the image file
            size: Optional size for the pixmap
        Returns:
            QPixmap object
        """
        cache_key = f"{image_name}_{size.width() if size else 0}x{size.height() if size else 0}"
        
        if cache_key in self._pixmap_cache:
            return self._pixmap_cache[cache_key]
        
        # Find image file
        image_path = self.find_image_file(image_name)
        if not image_path:
            # Return empty pixmap if not found
            pixmap = QPixmap()
            self._pixmap_cache[cache_key] = pixmap
            return pixmap
        
        # Load pixmap
        pixmap = QPixmap(image_path)
        
        # Scale if size is specified and pixmap is valid
        if size and not pixmap.isNull():
            pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self._pixmap_cache[cache_key] = pixmap
        return pixmap
    
    def get_image(self, image_name: str) -> Optional[QImage]:
        """
        Get a QImage by name
        Args:
            image_name: Name of the image file
        Returns:
            QImage object or None if not found
        """
        image_path = self.find_image_file(image_name)
        if not image_path:
            return None
        
        return QImage(image_path)
    
    def clear_cache(self):
        """Clear all cached images"""
        self._icon_cache.clear()
        self._pixmap_cache.clear()
    
    def preload_icons(self, icon_names: list):
        """
        Preload a list of icons into cache
        Args:
            icon_names: List of icon names to preload
        """
        for icon_name in icon_names:
            self.get_icon(icon_name)
    
    def get_available_images(self) -> list:
        """
        Get list of available image files in resource paths
        Returns:
            List of image file names
        """
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.ico', '.svg'}
        available_images = []
        
        for resource_path in self._resource_paths:
            if os.path.exists(resource_path):
                for file_name in os.listdir(resource_path):
                    if any(file_name.lower().endswith(ext) for ext in image_extensions):
                        available_images.append(file_name)
        
        return list(set(available_images))  # Remove duplicates


class ImageListFromResource:
    """Image list class for backward compatibility"""
    
    def __init__(self):
        self._bitmaps = {}
        self._image_names = []
    
    def get_image_index_by_name(self, image_name: str) -> int:
        """
        Get index of image by name
        Args:
            image_name: Name of the image
        Returns:
            Index of the image or -1 if not found
        """
        if image_name in self._image_names:
            return self._image_names.index(image_name)
        return -1
    
    def add_image(self, image_name: str, pixmap: QPixmap = None):
        """
        Add an image to the list
        Args:
            image_name: Name of the image
            pixmap: Optional QPixmap to add
        """
        if image_name not in self._image_names:
            self._image_names.append(image_name)
            if pixmap:
                self._bitmaps[image_name] = pixmap
    
    def get_pixmap(self, image_name: str) -> Optional[QPixmap]:
        """
        Get pixmap by name
        Args:
            image_name: Name of the image
        Returns:
            QPixmap or None if not found
        """
        return self._bitmaps.get(image_name)
    
    def clear(self):
        """Clear all images"""
        self._bitmaps.clear()
        self._image_names.clear()
    
    def count(self) -> int:
        """Get number of images in the list"""
        return len(self._image_names)


# Global image helper instance
_global_image_helper: Optional[ImageHelper] = None


def get_image_helper() -> ImageHelper:
    """Get the global image helper instance"""
    global _global_image_helper
    if _global_image_helper is None:
        _global_image_helper = ImageHelper()
    return _global_image_helper


# Backward compatibility functions
def GetIcon(image_name: str, size: Optional[QSize] = None) -> QIcon:
    """Get icon (backward compatibility)"""
    return get_image_helper().get_icon(image_name, size)


def GetPixmap(image_name: str, size: Optional[QSize] = None) -> QPixmap:
    """Get pixmap (backward compatibility)"""
    return get_image_helper().get_pixmap(image_name, size)


def GetImage(image_name: str) -> Optional[QImage]:
    """Get image (backward compatibility)"""
    return get_image_helper().get_image(image_name)


def CreateImageListFromResource() -> ImageListFromResource:
    """Create image list from resource (backward compatibility)"""
    return ImageListFromResource()
