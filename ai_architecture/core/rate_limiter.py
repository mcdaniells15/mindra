import time
import asyncio
from typing import Dict, Optional, Any, Callable, Protocol
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
import threading
from asyncio import Lock
from collections import deque, defaultdict
from abc import ABC, abstractmethod
from ..config import Config

@dataclass
class Bucket:
    """Token bucket for rate limiting."""
    tokens: float
    last_update: float
    max_tokens: int
    rate: float  # tokens per second

@dataclass
class RateLimitInfo:
    """Rate limit information."""
    remaining: int
    reset_time: float
    limit: int
    window: int

class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str, retry_after: float):
        self.retry_after = retry_after
        super().__init__(message)

class RateLimiterInterface(ABC):
    """Abstract base class for rate limiters."""
    
    @abstractmethod
    async def acquire(
        self,
        key: str,
        namespace: Optional[str] = None,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> tuple[bool, RateLimitInfo]:
        """Acquire a rate limit token."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Cleanup resources."""
        pass

class LocalRateLimiter(RateLimiterInterface):
    """In-memory rate limiter using token bucket algorithm."""
    
    def __init__(self, default_limit: int = 100, default_window: int = 60):
        self.default_limit = default_limit
        self.default_window = default_window
        self._buckets: Dict[str, tuple[float, float, float]] = {}  # (tokens, last_update, rate)
        self._lock = Lock()
        
        # LRU cache for cleanup
        self._last_accessed = deque(maxlen=1000)
        self._cleanup_threshold = max(100, default_limit * 2)
    
    def _get_bucket_key(self, key: str, namespace: Optional[str] = None) -> str:
        """Generate bucket key with optional namespace."""
        return f"{namespace}:{key}" if namespace else key
    
    def _get_bucket(
        self,
        key: str,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> tuple[float, float, float]:
        """Get or create a token bucket."""
        limit = limit or self.default_limit
        window = window or self.default_window
        rate = limit / window
        
        if key not in self._buckets:
            self._buckets[key] = (float(limit), time.time(), rate)
        return self._buckets[key]
    
    def _refill_tokens(
        self,
        tokens: float,
        last_update: float,
        rate: float,
        max_tokens: int
    ) -> tuple[float, float]:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - last_update
        new_tokens = min(max_tokens, tokens + (elapsed * rate))
        return new_tokens, now
    
    async def acquire(
        self,
        key: str,
        namespace: Optional[str] = None,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> tuple[bool, RateLimitInfo]:
        """Acquire a rate limit token."""
        bucket_key = self._get_bucket_key(key, namespace)
        limit = limit or self.default_limit
        window = window or self.default_window
        
        async with self._lock:
            tokens, last_update, rate = self._get_bucket(bucket_key, limit, window)
            tokens, now = self._refill_tokens(tokens, last_update, rate, limit)
            
            if tokens >= 1:
                self._buckets[bucket_key] = (tokens - 1, now, rate)
                return True, RateLimitInfo(
                    remaining=int(tokens - 1),
                    reset_time=now + (1 / rate),
                    limit=limit,
                    window=window
                )
            
            wait_time = (1 - tokens) / rate
            return False, RateLimitInfo(
                remaining=0,
                reset_time=now + wait_time,
                limit=limit,
                window=window
            )
    
    async def close(self) -> None:
        """Cleanup resources."""
        self._buckets.clear()
        self._last_accessed.clear()

# Global rate limiter instance
_rate_limiter: Optional[RateLimiterInterface] = None

def set_rate_limiter(limiter: RateLimiterInterface) -> None:
    """Set the global rate limiter implementation."""
    global _rate_limiter
    _rate_limiter = limiter

def get_rate_limiter() -> RateLimiterInterface:
    """Get the current rate limiter implementation."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = LocalRateLimiter()
    return _rate_limiter

def rate_limit(
    key: str = "default",
    max_requests: int = 100,
    time_window: int = 60,
    namespace: Optional[str] = None
):
    """Decorator for rate limiting async functions.
    
    Args:
        key: Rate limit key or key template
        max_requests: Maximum requests per time window
        time_window: Time window in seconds
        namespace: Optional namespace for grouping keys
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate dynamic key if needed
            actual_key = key.format(*args, **kwargs) if "{" in key else key
            
            # Use local rate limiting
            limiter = get_rate_limiter()
            success, info = await limiter.acquire(
                actual_key,
                namespace=namespace,
                limit=max_requests,
                window=time_window
            )
            
            if not success:
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Try again in {info.reset_time - time.time():.1f} seconds",
                    retry_after=info.reset_time - time.time()
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting."""
    tokens: float
    last_update: float
    max_tokens: int
    refill_rate: float  # tokens per second

class RateLimiter:
    """Implements a token bucket rate limiter with multiple limit types."""
    
    def __init__(self):
        self.global_bucket = RateLimitBucket(
            tokens=Config.RATE_LIMIT_SETTINGS["global"]["limit"],
            last_update=time.time(),
            max_tokens=Config.RATE_LIMIT_SETTINGS["global"]["limit"],
            refill_rate=Config.RATE_LIMIT_SETTINGS["global"]["limit"] / 60
        )
        
        self.user_buckets: Dict[str, Dict[str, RateLimitBucket]] = defaultdict(dict)
        self.ip_buckets: Dict[str, Dict[str, RateLimitBucket]] = defaultdict(dict)
        self._lock = threading.Lock()
        
    def _refill_bucket(self, bucket: RateLimitBucket) -> None:
        """Refill tokens in the bucket based on time elapsed."""
        now = time.time()
        time_passed = now - bucket.last_update
        bucket.tokens = min(
            bucket.max_tokens,
            bucket.tokens + time_passed * bucket.refill_rate
        )
        bucket.last_update = now
        
    async def check_rate_limit(self, user_id: str, ip: str) -> bool:
        """Check if the request should be rate limited."""
        with self._lock:
            # Check global limit
            self._refill_bucket(self.global_bucket)
            if self.global_bucket.tokens < 1:
                return False
                
            # Check user limits
            if user_id not in self.user_buckets:
                self.user_buckets[user_id] = {
                    "minute": RateLimitBucket(
                        tokens=Config.RATE_LIMIT_SETTINGS["user"]["limit_per_minute"],
                        last_update=time.time(),
                        max_tokens=Config.RATE_LIMIT_SETTINGS["user"]["limit_per_minute"],
                        refill_rate=Config.RATE_LIMIT_SETTINGS["user"]["limit_per_minute"] / 60
                    ),
                    "hour": RateLimitBucket(
                        tokens=Config.RATE_LIMIT_SETTINGS["user"]["limit_per_hour"],
                        last_update=time.time(),
                        max_tokens=Config.RATE_LIMIT_SETTINGS["user"]["limit_per_hour"],
                        refill_rate=Config.RATE_LIMIT_SETTINGS["user"]["limit_per_hour"] / 3600
                    ),
                    "day": RateLimitBucket(
                        tokens=Config.RATE_LIMIT_SETTINGS["user"]["limit_per_day"],
                        last_update=time.time(),
                        max_tokens=Config.RATE_LIMIT_SETTINGS["user"]["limit_per_day"],
                        refill_rate=Config.RATE_LIMIT_SETTINGS["user"]["limit_per_day"] / 86400
                    )
                }
                
            for bucket in self.user_buckets[user_id].values():
                self._refill_bucket(bucket)
                if bucket.tokens < 1:
                    return False
                    
            # Check IP limits
            if ip not in self.ip_buckets:
                self.ip_buckets[ip] = {
                    "minute": RateLimitBucket(
                        tokens=Config.RATE_LIMIT_SETTINGS["ip"]["limit_per_minute"],
                        last_update=time.time(),
                        max_tokens=Config.RATE_LIMIT_SETTINGS["ip"]["limit_per_minute"],
                        refill_rate=Config.RATE_LIMIT_SETTINGS["ip"]["limit_per_minute"] / 60
                    ),
                    "hour": RateLimitBucket(
                        tokens=Config.RATE_LIMIT_SETTINGS["ip"]["limit_per_hour"],
                        last_update=time.time(),
                        max_tokens=Config.RATE_LIMIT_SETTINGS["ip"]["limit_per_hour"],
                        refill_rate=Config.RATE_LIMIT_SETTINGS["ip"]["limit_per_hour"] / 3600
                    ),
                    "day": RateLimitBucket(
                        tokens=Config.RATE_LIMIT_SETTINGS["ip"]["limit_per_day"],
                        last_update=time.time(),
                        max_tokens=Config.RATE_LIMIT_SETTINGS["ip"]["limit_per_day"],
                        refill_rate=Config.RATE_LIMIT_SETTINGS["ip"]["limit_per_day"] / 86400
                    )
                }
                
            for bucket in self.ip_buckets[ip].values():
                self._refill_bucket(bucket)
                if bucket.tokens < 1:
                    return False
                    
            # If we get here, consume tokens from all buckets
            self.global_bucket.tokens -= 1
            for bucket in self.user_buckets[user_id].values():
                bucket.tokens -= 1
            for bucket in self.ip_buckets[ip].values():
                bucket.tokens -= 1
                
            return True
            
    async def get_remaining_tokens(self, user_id: str, ip: str) -> Dict[str, int]:
        """Get remaining tokens for all buckets."""
        with self._lock:
            return {
                "global": int(self.global_bucket.tokens),
                "user_minute": int(self.user_buckets[user_id]["minute"].tokens),
                "user_hour": int(self.user_buckets[user_id]["hour"].tokens),
                "user_day": int(self.user_buckets[user_id]["day"].tokens),
                "ip_minute": int(self.ip_buckets[ip]["minute"].tokens),
                "ip_hour": int(self.ip_buckets[ip]["hour"].tokens),
                "ip_day": int(self.ip_buckets[ip]["day"].tokens)
            }

__all__ = [
    'Bucket',
    'RateLimitInfo',
    'RateLimitExceeded',
    'RateLimiterInterface',
    'LocalRateLimiter',
    'rate_limit',
    'set_rate_limiter',
    'get_rate_limiter'
] 