"""Simple in-memory cache with TTL."""

import time
from typing import Dict, Any, Optional, Callable
from functools import wraps


class TTLCache:
    """Simple TTL cache implementation."""
    
    def __init__(self):
        """Initialize cache."""
        self._cache: Dict[str, tuple[Any, float]] = {}
    
    def get(self, key: str, ttl: float) -> Optional[Any]:
        """Get value from cache if not expired.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            Cached value or None if expired/not found
        """
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        if time.time() - timestamp > ttl:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())
    
    def invalidate(self, key: str) -> None:
        """Invalidate a cache key.
        
        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


# Global cache instance
_cache = TTLCache()


def cached(ttl: float = 300.0):
    """Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached_value = _cache.get(cache_key, ttl)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            _cache.set(cache_key, result)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached_value = _cache.get(cache_key, ttl)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result)
            return result
        
        # Return appropriate wrapper based on whether function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def get_cache() -> TTLCache:
    """Get global cache instance.
    
    Returns:
        TTLCache instance
    """
    return _cache
