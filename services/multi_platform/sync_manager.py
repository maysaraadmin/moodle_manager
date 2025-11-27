#!/usr/bin/env python3
"""
Multi-Platform Data Synchronization Manager for Moodle Manager
Handles data synchronization across multiple Moodle platforms
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from core.data_models_multi import MoodlePlatform, MultiPlatformManager
from services.multi_platform.auth_manager import MultiPlatformAuthManager

logger = logging.getLogger(__name__)


class SyncStatus:
    """Synchronization status tracking"""
    IDLE = "idle"
    SYNCING = "syncing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class SyncOperation:
    """Represents a synchronization operation"""
    
    def __init__(self, operation_id: str, platform_ids: List[str], sync_type: str):
        self.id = operation_id
        self.platform_ids = platform_ids
        self.sync_type = sync_type
        self.status = SyncStatus.IDLE
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.progress = 0.0
        self.current_platform: Optional[str] = None
        self.results: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.cancelled = False
        self.lock = threading.Lock()
    
    def start(self):
        """Start the sync operation"""
        with self.lock:
            self.status = SyncStatus.SYNCING
            self.start_time = datetime.now()
    
    def complete(self):
        """Complete the sync operation"""
        with self.lock:
            self.status = SyncStatus.COMPLETED
            self.end_time = datetime.now()
            self.progress = 100.0
    
    def error(self, error_message: str):
        """Mark operation as error"""
        with self.lock:
            self.status = SyncStatus.ERROR
            self.end_time = datetime.now()
            self.errors.append(error_message)
    
    def cancel(self):
        """Cancel the sync operation"""
        with self.lock:
            self.status = SyncStatus.CANCELLED
            self.end_time = datetime.now()
            self.cancelled = True
    
    def update_progress(self, progress: float, current_platform: str = None):
        """Update operation progress"""
        with self.lock:
            self.progress = progress
            if current_platform:
                self.current_platform = current_platform
    
    def get_duration(self) -> Optional[timedelta]:
        """Get operation duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class MultiPlatformSyncManager:
    """Manages data synchronization across multiple Moodle platforms"""
    
    def __init__(self, multi_platform_manager: MultiPlatformManager, auth_manager: MultiPlatformAuthManager):
        self.multi_platform_manager = multi_platform_manager
        self.auth_manager = auth_manager
        self.active_operations: Dict[str, SyncOperation] = {}
        self.sync_history: List[SyncOperation] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.sync_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_expiry = timedelta(minutes=30)
        self.last_cache_cleanup = datetime.now()
    
    def create_sync_operation(self, platform_ids: List[str], sync_type: str) -> str:
        """Create a new sync operation"""
        import uuid
        operation_id = str(uuid.uuid4())
        
        operation = SyncOperation(operation_id, platform_ids, sync_type)
        self.active_operations[operation_id] = operation
        
        return operation_id
    
    def start_sync_operation(self, operation_id: str) -> bool:
        """Start a sync operation"""
        if operation_id not in self.active_operations:
            return False
        
        operation = self.active_operations[operation_id]
        operation.start()
        
        # Submit to thread pool
        future = self.executor.submit(self._execute_sync_operation, operation)
        
        return True
    
    def cancel_sync_operation(self, operation_id: str) -> bool:
        """Cancel a sync operation"""
        if operation_id not in self.active_operations:
            return False
        
        operation = self.active_operations[operation_id]
        operation.cancel()
        
        return True
    
    def get_operation_status(self, operation_id: str) -> Optional[SyncOperation]:
        """Get sync operation status"""
        return self.active_operations.get(operation_id)
    
    def get_all_operations(self) -> List[SyncOperation]:
        """Get all sync operations (active and completed)"""
        operations = list(self.active_operations.values())
        operations.extend(self.sync_history)
        return operations
    
    def _execute_sync_operation(self, operation: SyncOperation):
        """Execute a sync operation"""
        try:
            if operation.sync_type == "full":
                self._execute_full_sync(operation)
            elif operation.sync_type == "users":
                self._execute_users_sync(operation)
            elif operation.sync_type == "courses":
                self._execute_courses_sync(operation)
            elif operation.sync_type == "categories":
                self._execute_categories_sync(operation)
            else:
                operation.error(f"Unknown sync type: {operation.sync_type}")
                
        except Exception as e:
            logger.error(f"Sync operation {operation.id} failed: {e}")
            operation.error(str(e))
        
        finally:
            # Move to history
            if operation.id in self.active_operations:
                del self.active_operations[operation.id]
                self.sync_history.append(operation)
    
    def _execute_full_sync(self, operation: SyncOperation):
        """Execute full synchronization"""
        total_platforms = len(operation.platform_ids)
        
        for i, platform_id in enumerate(operation.platform_ids):
            if operation.cancelled:
                operation.cancel()
                return
            
            platform = self.multi_platform_manager.get_platform(platform_id)
            if not platform:
                operation.error(f"Platform {platform_id} not found")
                continue
            
            try:
                operation.update_progress((i / total_platforms) * 100, platform.name)
                
                # Sync users
                self._sync_platform_users(platform_id, operation)
                
                # Sync courses
                self._sync_platform_courses(platform_id, operation)
                
                # Sync categories
                self._sync_platform_categories(platform_id, operation)
                
            except Exception as e:
                logger.error(f"Error syncing platform {platform.name}: {e}")
                operation.errors.append(f"Error syncing {platform.name}: {str(e)}")
        
        operation.complete()
    
    def _execute_users_sync(self, operation: SyncOperation):
        """Execute users synchronization"""
        total_platforms = len(operation.platform_ids)
        
        for i, platform_id in enumerate(operation.platform_ids):
            if operation.cancelled:
                operation.cancel()
                return
            
            platform = self.multi_platform_manager.get_platform(platform_id)
            if not platform:
                continue
            
            try:
                operation.update_progress((i / total_platforms) * 100, platform.name)
                self._sync_platform_users(platform_id, operation)
                
            except Exception as e:
                logger.error(f"Error syncing users for {platform.name}: {e}")
                operation.errors.append(f"Error syncing users for {platform.name}: {str(e)}")
        
        operation.complete()
    
    def _execute_courses_sync(self, operation: SyncOperation):
        """Execute courses synchronization"""
        total_platforms = len(operation.platform_ids)
        
        for i, platform_id in enumerate(operation.platform_ids):
            if operation.cancelled:
                operation.cancel()
                return
            
            platform = self.multi_platform_manager.get_platform(platform_id)
            if not platform:
                continue
            
            try:
                operation.update_progress((i / total_platforms) * 100, platform.name)
                self._sync_platform_courses(platform_id, operation)
                
            except Exception as e:
                logger.error(f"Error syncing courses for {platform.name}: {e}")
                operation.errors.append(f"Error syncing courses for {platform.name}: {str(e)}")
        
        operation.complete()
    
    def _execute_categories_sync(self, operation: SyncOperation):
        """Execute categories synchronization"""
        total_platforms = len(operation.platform_ids)
        
        for i, platform_id in enumerate(operation.platform_ids):
            if operation.cancelled:
                operation.cancel()
                return
            
            platform = self.multi_platform_manager.get_platform(platform_id)
            if not platform:
                continue
            
            try:
                operation.update_progress((i / total_platforms) * 100, platform.name)
                self._sync_platform_categories(platform_id, operation)
                
            except Exception as e:
                logger.error(f"Error syncing categories for {platform.name}: {e}")
                operation.errors.append(f"Error syncing categories for {platform.name}: {str(e)}")
        
        operation.complete()
    
    def _sync_platform_users(self, platform_id: str, operation: SyncOperation):
        """Sync users from a platform"""
        try:
            # Check cache first
            cache_key = f"{platform_id}_users"
            if self._is_cache_valid(cache_key):
                cached_data = self.sync_cache.get(cache_key, {}).get('data', [])
                operation.results[f"{platform_id}_users"] = cached_data
                return
            
            # Get users from platform
            success, users = self.auth_manager.get_platform_users(platform_id)
            
            if success:
                # Cache the results
                self.sync_cache[cache_key] = {
                    'data': users,
                    'timestamp': datetime.now()
                }
                
                operation.results[f"{platform_id}_users"] = users
                logger.info(f"Synced {len(users)} users from platform {platform_id}")
            else:
                operation.errors.append(f"Failed to sync users from platform {platform_id}: {users}")
                
        except Exception as e:
            logger.error(f"Error syncing users from platform {platform_id}: {e}")
            operation.errors.append(f"Error syncing users from platform {platform_id}: {str(e)}")
    
    def _sync_platform_courses(self, platform_id: str, operation: SyncOperation):
        """Sync courses from a platform"""
        try:
            # Check cache first
            cache_key = f"{platform_id}_courses"
            if self._is_cache_valid(cache_key):
                cached_data = self.sync_cache.get(cache_key, {}).get('data', [])
                operation.results[f"{platform_id}_courses"] = cached_data
                return
            
            # Get courses from platform
            success, courses = self.auth_manager.get_platform_courses(platform_id)
            
            if success:
                # Cache the results
                self.sync_cache[cache_key] = {
                    'data': courses,
                    'timestamp': datetime.now()
                }
                
                operation.results[f"{platform_id}_courses"] = courses
                logger.info(f"Synced {len(courses)} courses from platform {platform_id}")
            else:
                operation.errors.append(f"Failed to sync courses from platform {platform_id}: {courses}")
                
        except Exception as e:
            logger.error(f"Error syncing courses from platform {platform_id}: {e}")
            operation.errors.append(f"Error syncing courses from platform {platform_id}: {str(e)}")
    
    def _sync_platform_categories(self, platform_id: str, operation: SyncOperation):
        """Sync categories from a platform"""
        try:
            # Check cache first
            cache_key = f"{platform_id}_categories"
            if self._is_cache_valid(cache_key):
                cached_data = self.sync_cache.get(cache_key, {}).get('data', [])
                operation.results[f"{platform_id}_categories"] = cached_data
                return
            
            # Get categories from platform
            success, categories = self.auth_manager.get_platform_categories(platform_id)
            
            if success:
                # Cache the results
                self.sync_cache[cache_key] = {
                    'data': categories,
                    'timestamp': datetime.now()
                }
                
                operation.results[f"{platform_id}_categories"] = categories
                logger.info(f"Synced {len(categories)} categories from platform {platform_id}")
            else:
                operation.errors.append(f"Failed to sync categories from platform {platform_id}: {categories}")
                
        except Exception as e:
            logger.error(f"Error syncing categories from platform {platform_id}: {e}")
            operation.errors.append(f"Error syncing categories from platform {platform_id}: {str(e)}")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.sync_cache:
            return False
        
        cache_entry = self.sync_cache[cache_key]
        timestamp = cache_entry.get('timestamp')
        
        if not timestamp:
            return False
        
        return datetime.now() - timestamp < self.cache_expiry
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, entry in self.sync_cache.items():
            timestamp = entry.get('timestamp')
            if timestamp and current_time - timestamp > self.cache_expiry:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.sync_cache[key]
        
        self.last_cache_cleanup = current_time
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_cached_data(self, platform_id: str, data_type: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached data for a platform"""
        cache_key = f"{platform_id}_{data_type}"
        
        if self._is_cache_valid(cache_key):
            return self.sync_cache.get(cache_key, {}).get('data')
        
        return None
    
    def invalidate_cache(self, platform_id: str = None, data_type: str = None):
        """Invalidate cache entries"""
        if platform_id and data_type:
            # Invalidate specific entry
            cache_key = f"{platform_id}_{data_type}"
            if cache_key in self.sync_cache:
                del self.sync_cache[cache_key]
        elif platform_id:
            # Invalidate all entries for a platform
            keys_to_remove = [key for key in self.sync_cache.keys() if key.startswith(f"{platform_id}_")]
            for key in keys_to_remove:
                del self.sync_cache[key]
        else:
            # Invalidate all cache
            self.sync_cache.clear()
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        total_operations = len(self.active_operations) + len(self.sync_history)
        active_operations = len(self.active_operations)
        
        # Calculate success rate
        completed_operations = [op for op in self.sync_history if op.status == SyncStatus.COMPLETED]
        error_operations = [op for op in self.sync_history if op.status == SyncStatus.ERROR]
        
        success_rate = 0.0
        if len(self.sync_history) > 0:
            success_rate = (len(completed_operations) / len(self.sync_history)) * 100
        
        # Cache statistics
        cache_size = len(self.sync_cache)
        cache_entries = list(self.sync_cache.values())
        total_cached_items = sum(len(entry.get('data', [])) for entry in cache_entries)
        
        return {
            'total_operations': total_operations,
            'active_operations': active_operations,
            'completed_operations': len(completed_operations),
            'error_operations': len(error_operations),
            'success_rate': success_rate,
            'cache_size': cache_size,
            'total_cached_items': total_cached_items,
            'last_cache_cleanup': self.last_cache_cleanup.isoformat() if self.last_cache_cleanup else None
        }
    
    def sync_all_platforms(self) -> str:
        """Start synchronization for all active platforms"""
        active_platforms = self.multi_platform_manager.get_active_platforms()
        platform_ids = [p.id for p in active_platforms]
        
        if not platform_ids:
            raise ValueError("No active platforms to sync")
        
        operation_id = self.create_sync_operation(platform_ids, "full")
        self.start_sync_operation(operation_id)
        
        return operation_id
    
    def sync_platform_users(self, platform_id: str) -> str:
        """Sync users for a specific platform"""
        operation_id = self.create_sync_operation([platform_id], "users")
        self.start_sync_operation(operation_id)
        
        return operation_id
    
    def sync_platform_courses(self, platform_id: str) -> str:
        """Sync courses for a specific platform"""
        operation_id = self.create_sync_operation([platform_id], "courses")
        self.start_sync_operation(operation_id)
        
        return operation_id
    
    def sync_platform_categories(self, platform_id: str) -> str:
        """Sync categories for a specific platform"""
        operation_id = self.create_sync_operation([platform_id], "categories")
        self.start_sync_operation(operation_id)
        
        return operation_id
    
    def export_sync_data(self, file_path: str, platform_ids: List[str] = None, data_types: List[str] = None) -> bool:
        """Export synchronized data to file"""
        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'version': '1.0',
                'platforms': {}
            }
            
            platforms_to_export = platform_ids or [p.id for p in self.multi_platform_manager.get_all_platforms()]
            data_types_to_export = data_types or ['users', 'courses', 'categories']
            
            for platform_id in platforms_to_export:
                platform = self.multi_platform_manager.get_platform(platform_id)
                if not platform:
                    continue
                
                platform_data = {
                    'name': platform.name,
                    'url': platform.url,
                    'data': {}
                }
                
                for data_type in data_types_to_export:
                    cached_data = self.get_cached_data(platform_id, data_type)
                    if cached_data:
                        platform_data['data'][data_type] = cached_data
                
                export_data['platforms'][platform_id] = platform_data
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting sync data: {e}")
            return False
    
    def shutdown(self):
        """Shutdown the sync manager"""
        # Cancel all active operations
        for operation_id in list(self.active_operations.keys()):
            self.cancel_sync_operation(operation_id)
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        logger.info("Multi-platform sync manager shutdown complete")
