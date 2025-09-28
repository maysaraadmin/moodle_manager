"""
RTTI (Run-Time Type Information) helper for LMS Explorer
Handles reflection and property access for objects
"""

import inspect
from typing import Any, Optional, Union, Dict, List


class RTTIHelper:
    """Helper class for RTTI-like functionality in Python"""
    
    def __init__(self):
        self._property_cache: Dict[str, Dict[str, Any]] = {}
    
    def get_property_value(self, instance: Any, prop_name: str) -> str:
        """
        Get property value from an instance as string
        Args:
            instance: The object instance
            prop_name: Name of the property
        Returns:
            Property value as string, empty string if not found
        """
        if instance is None:
            return ""
        
        try:
            # Try to get property using getattr
            if hasattr(instance, prop_name):
                value = getattr(instance, prop_name)
                
                # Handle different types
                if value is None:
                    return ""
                elif isinstance(value, str):
                    return value
                elif isinstance(value, (int, float)):
                    return str(value)
                elif isinstance(value, bool):
                    return "True" if value else "False"
                elif hasattr(value, '__str__'):
                    return str(value)
                else:
                    return ""
            
            # Try to get property using getter method
            getter_name = f"get_{prop_name}"
            if hasattr(instance, getter_name):
                getter = getattr(instance, getter_name)
                if callable(getter):
                    value = getter()
                    if value is None:
                        return ""
                    return str(value)
            
            return ""
            
        except Exception as e:
            return f"Error: {e}"
    
    def get_property_values(self, instance: Any) -> Dict[str, str]:
        """
        Get all property values from an instance
        Args:
            instance: The object instance
        Returns:
            Dictionary of property names and values
        """
        if instance is None:
            return {}
        
        result = {}
        
        try:
            # Get all attributes
            for attr_name in dir(instance):
                # Skip private attributes and methods
                if attr_name.startswith('_'):
                    continue
                
                attr_value = getattr(instance, attr_name)
                
                # Skip methods and callable objects
                if callable(attr_value):
                    continue
                
                # Get property value
                result[attr_name] = self.get_property_value(instance, attr_name)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_properties_info(self, instance: Any) -> List[Dict[str, Any]]:
        """
        Get detailed information about object properties
        Args:
            instance: The object instance
        Returns:
            List of property information dictionaries
        """
        if instance is None:
            return []
        
        properties = []
        
        try:
            # Use inspect to get members
            for name, value in inspect.getmembers(instance):
                # Skip private attributes and methods
                if name.startswith('_'):
                    continue
                
                if callable(value):
                    continue
                
                prop_info = {
                    'name': name,
                    'type': type(value).__name__,
                    'value': value,
                    'value_str': str(value),
                    'is_readable': True,
                    'is_writable': not name.startswith('_') and not callable(value)
                }
                
                properties.append(prop_info)
        
        except Exception as e:
            properties.append({
                'name': 'error',
                'type': 'Error',
                'value': e,
                'value_str': str(e),
                'is_readable': False,
                'is_writable': False
            })
        
        return properties
    
    def set_property_value(self, instance: Any, prop_name: str, value: Any) -> bool:
        """
        Set property value on an instance
        Args:
            instance: The object instance
            prop_name: Name of the property
            value: Value to set
        Returns:
            True if successful, False otherwise
        """
        if instance is None:
            return False
        
        try:
            # Try to set property using setattr
            if hasattr(instance, prop_name):
                setattr(instance, prop_name, value)
                return True
            
            # Try to set property using setter method
            setter_name = f"set_{prop_name}"
            if hasattr(instance, setter_name):
                setter = getattr(instance, setter_name)
                if callable(setter):
                    setter(value)
                    return True
            
            return False
            
        except Exception:
            return False
    
    def has_property(self, instance: Any, prop_name: str) -> bool:
        """
        Check if instance has a property
        Args:
            instance: The object instance
            prop_name: Name of the property
        Returns:
            True if property exists, False otherwise
        """
        if instance is None:
            return False
        
        return hasattr(instance, prop_name) or hasattr(instance, f"get_{prop_name}")
    
    def get_method_info(self, instance: Any) -> List[Dict[str, Any]]:
        """
        Get information about object methods
        Args:
            instance: The object instance
        Returns:
            List of method information dictionaries
        """
        if instance is None:
            return []
        
        methods = []
        
        try:
            # Use inspect to get methods
            for name, value in inspect.getmembers(instance):
                # Skip private methods
                if name.startswith('_'):
                    continue
                
                if callable(value):
                    # Get method signature
                    try:
                        sig = inspect.signature(value)
                        params = list(sig.parameters.keys())
                    except:
                        params = []
                    
                    method_info = {
                        'name': name,
                        'parameters': params,
                        'doc': inspect.getdoc(value) or "",
                        'is_method': True
                    }
                    
                    methods.append(method_info)
        
        except Exception as e:
            methods.append({
                'name': 'error',
                'parameters': [],
                'doc': str(e),
                'is_method': False
            })
        
        return methods
    
    def get_class_info(self, instance: Any) -> Dict[str, Any]:
        """
        Get comprehensive class information
        Args:
            instance: The object instance
        Returns:
            Dictionary containing class information
        """
        if instance is None:
            return {}
        
        try:
            class_info = {
                'class_name': instance.__class__.__name__,
                'module': instance.__class__.__module__,
                'properties': self.get_properties_info(instance),
                'methods': self.get_method_info(instance),
                'doc': inspect.getdoc(instance) or "",
                'bases': [base.__name__ for base in instance.__class__.__bases__]
            }
            
            return class_info
            
        except Exception as e:
            return {
                'class_name': 'Error',
                'module': '',
                'properties': [],
                'methods': [],
                'doc': str(e),
                'bases': []
            }
    
    def cache_properties(self, instance: Any, cache_key: str):
        """
        Cache property values for an instance
        Args:
            instance: The object instance
            cache_key: Key for caching
        """
        if instance is None:
            return
        
        self._property_cache[cache_key] = self.get_property_values(instance)
    
    def get_cached_properties(self, cache_key: str) -> Optional[Dict[str, str]]:
        """
        Get cached property values
        Args:
            cache_key: Cache key
        Returns:
            Cached properties or None if not found
        """
        return self._property_cache.get(cache_key)
    
    def clear_cache(self):
        """Clear the property cache"""
        self._property_cache.clear()


# Global RTTI helper instance
_global_rtti_helper: Optional[RTTIHelper] = None


def get_rtti_helper() -> RTTIHelper:
    """Get the global RTTI helper instance"""
    global _global_rtti_helper
    if _global_rtti_helper is None:
        _global_rtti_helper = RTTIHelper()
    return _global_rtti_helper


# Backward compatibility functions
def GetPropertyValue(instance: Any, prop_name: str) -> str:
    """Get property value (backward compatibility)"""
    return get_rtti_helper().get_property_value(instance, prop_name)


def GetPropertyValues(instance: Any) -> Dict[str, str]:
    """Get all property values (backward compatibility)"""
    return get_rtti_helper().get_property_values(instance)


def SetPropertyValue(instance: Any, prop_name: str, value: Any) -> bool:
    """Set property value (backward compatibility)"""
    return get_rtti_helper().set_property_value(instance, prop_name, value)
