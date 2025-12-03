"""
Cache Manager for AccountApp
Provides intelligent caching with TTL, invalidation strategies,
and cache statistics for improved performance.
"""

import logging
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from threading import Lock
import json

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a single cache entry with metadata"""
    
    def __init__(self, key: str, value: Any, ttl: int = 300):
        """
        Initialize cache entry
        
        Args:
            key: Cache key
            value: Cached value
            ttl: Time to live in seconds (default: 5 minutes)
        """
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl)
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.now() > self.expires_at
    
    def access(self) -> Any:
        """Access the cached value and update metadata"""
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value
    
    def refresh(self, ttl: int = 300):
        """Refresh the expiration time"""
        self.expires_at = datetime.now() + timedelta(seconds=ttl)


class CacheManager:
    """
    Intelligent caching system with:
    - Time-based expiration (TTL)
    - Manual invalidation
    - Cache statistics
    - Thread-safe operations
    - Namespace support
    """
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        Initialize cache manager
        
        Args:
            default_ttl: Default time to live in seconds
            max_size: Maximum number of cache entries
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
        self.max_size = max_size
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'invalidations': 0
        }
        
        logger.info(f"Cache Manager initialized (TTL: {default_ttl}s, Max Size: {max_size})")
    
    def _make_key(self, namespace: str, key: str) -> str:
        """Create a namespaced cache key"""
        return f"{namespace}:{key}"
    
    def _cleanup_expired(self):
        """Remove expired entries from cache"""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self.stats['evictions'] += 1
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _enforce_size_limit(self):
        """Enforce maximum cache size by removing least recently accessed items"""
        with self._lock:
            if len(self._cache) > self.max_size:
                # Sort by last accessed time and remove oldest
                sorted_entries = sorted(
                    self._cache.items(),
                    key=lambda x: x[1].last_accessed
                )
                
                num_to_remove = len(self._cache) - self.max_size
                for key, _ in sorted_entries[:num_to_remove]:
                    del self._cache[key]
                    self.stats['evictions'] += 1
                
                logger.debug(f"Evicted {num_to_remove} cache entries to enforce size limit")
    
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            namespace: Cache namespace
        
        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._make_key(namespace, key)
        
        with self._lock:
            entry = self._cache.get(cache_key)
            
            if entry is None:
                self.stats['misses'] += 1
                return None
            
            if entry.is_expired():
                del self._cache[cache_key]
                self.stats['misses'] += 1
                self.stats['evictions'] += 1
                return None
            
            self.stats['hits'] += 1
            return entry.access()
    
    def set(self, key: str, value: Any, namespace: str = "default",
            ttl: Optional[int] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            namespace: Cache namespace
            ttl: Time to live in seconds (uses default if None)
        """
        cache_key = self._make_key(namespace, key)
        ttl = ttl if ttl is not None else self.default_ttl
        
        with self._lock:
            self._cache[cache_key] = CacheEntry(cache_key, value, ttl)
        
        # Cleanup and enforce limits
        self._cleanup_expired()
        self._enforce_size_limit()
    
    def delete(self, key: str, namespace: str = "default") -> bool:
        """
        Delete a specific cache entry
        
        Args:
            key: Cache key
            namespace: Cache namespace
        
        Returns:
            True if entry was deleted, False if not found
        """
        cache_key = self._make_key(namespace, key)
        
        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                self.stats['invalidations'] += 1
                return True
            return False
    
    def invalidate_namespace(self, namespace: str):
        """
        Invalidate all entries in a namespace
        
        Args:
            namespace: Namespace to invalidate
        """
        prefix = f"{namespace}:"
        
        with self._lock:
            keys_to_delete = [
                key for key in self._cache.keys()
                if key.startswith(prefix)
            ]
            
            for key in keys_to_delete:
                del self._cache[key]
                self.stats['invalidations'] += 1
            
            if keys_to_delete:
                logger.info(f"Invalidated {len(keys_to_delete)} entries in namespace '{namespace}'")
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self.stats['invalidations'] += count
            logger.info(f"Cleared all cache entries ({count} items)")
    
    def get_or_set(self, key: str, factory: Callable[[], Any],
                   namespace: str = "default", ttl: Optional[int] = None) -> Any:
        """
        Get value from cache or compute and cache it
        
        Args:
            key: Cache key
            factory: Function to compute value if not cached
            namespace: Cache namespace
            ttl: Time to live in seconds
        
        Returns:
            Cached or computed value
        """
        value = self.get(key, namespace)
        
        if value is None:
            value = factory()
            self.set(key, value, namespace, ttl)
        
        return value
    
    def refresh(self, key: str, namespace: str = "default", ttl: Optional[int] = None):
        """
        Refresh the TTL of a cache entry
        
        Args:
            key: Cache key
            namespace: Cache namespace
            ttl: New TTL in seconds (uses default if None)
        """
        cache_key = self._make_key(namespace, key)
        ttl = ttl if ttl is not None else self.default_ttl
        
        with self._lock:
            entry = self._cache.get(cache_key)
            if entry and not entry.is_expired():
                entry.refresh(ttl)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': f"{hit_rate:.2f}%",
                'evictions': self.stats['evictions'],
                'invalidations': self.stats['invalidations'],
                'total_requests': total_requests
            }
    
    def get_info(self, key: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        """
        Get information about a cache entry
        
        Args:
            key: Cache key
            namespace: Cache namespace
        
        Returns:
            Dictionary with entry information or None
        """
        cache_key = self._make_key(namespace, key)
        
        with self._lock:
            entry = self._cache.get(cache_key)
            
            if entry is None:
                return None
            
            return {
                'key': key,
                'namespace': namespace,
                'created_at': entry.created_at.isoformat(),
                'expires_at': entry.expires_at.isoformat(),
                'last_accessed': entry.last_accessed.isoformat(),
                'access_count': entry.access_count,
                'is_expired': entry.is_expired(),
                'size_bytes': len(json.dumps(entry.value)) if entry.value else 0
            }


# ==================== Global Cache Instance ====================

# Create a global cache instance for application-wide use
_global_cache = None


def get_cache() -> CacheManager:
    """Get the global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager(default_ttl=300, max_size=1000)
    return _global_cache


# ==================== Cache Decorators ====================

def cached(namespace: str = "default", ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator to cache function results
    
    Args:
        namespace: Cache namespace
        ttl: Time to live in seconds
        key_func: Optional function to generate cache key from arguments
    
    Usage:
        @cached(namespace="users", ttl=600)
        def get_user(user_id):
            # expensive operation
            return user_data
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name and arguments
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key, namespace)
            
            if result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return result
            
            # Compute and cache result
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, namespace, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(namespace: str):
    """
    Decorator to invalidate cache after function execution
    
    Usage:
        @invalidate_cache("users")
        def update_user(user_id, data):
            # update user
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache = get_cache()
            cache.invalidate_namespace(namespace)
            logger.debug(f"Invalidated cache namespace: {namespace}")
            return result
        return wrapper
    return decorator
