import time
import asyncio
from typing import Any, Optional, Dict, TypeVar, Callable
from functools import wraps
from threading import Lock

T = TypeVar('T')

class ResponseCache:
    """Simple thread-safe cache with TTL."""
    
    def __init__(self, default_ttl: int = 3600):
        """Initialize cache with default TTL in seconds."""
        self.default_ttl = default_ttl
        self._cache: Dict[str, tuple[Any, float]] = {}  # (value, expiry)
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if expiry > time.time():
                    return value
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        if value is None:  # Don't cache None values
            return
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
        with self._lock:
            self._cache[key] = (value, expiry)

    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()

# Global cache instance
response_cache = ResponseCache()

def cache_response(ttl: Optional[int] = None):
    """Cache decorator for both sync and async functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached = response_cache.get(key)
            if cached is not None:
                return cached
                
            # Get fresh result
            result = await func(*args, **kwargs)
            if result:  # Only cache non-empty results
                response_cache.set(key, result, ttl)
            return result
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached = response_cache.get(key)
            if cached is not None:
                return cached
                
            # Get fresh result
            result = func(*args, **kwargs)
            if result:  # Only cache non-empty results
                response_cache.set(key, result, ttl)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

__all__ = ['ResponseCache', 'response_cache', 'cache_response'] 