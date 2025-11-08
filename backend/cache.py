"""
Redis caching layer for ExamSensei
Provides caching for expensive operations and rate limiting
"""
import redis
import json
from typing import Any, Optional, Callable
from functools import wraps
from config import settings
from logger import logger
import hashlib


class CacheManager:
    """Redis cache manager with automatic serialization"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis unavailable, caching disabled: {e}")
            self.redis_client = None
            self.enabled = False
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [prefix]
        
        # Add positional args
        for arg in args:
            key_parts.append(str(arg))
        
        # Add keyword args (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        key = ":".join(key_parts)
        
        # Hash if too long
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        
        return key
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL (seconds)"""
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def increment(self, key: str, amount: int = 1, ttl: int = 60) -> int:
        """Increment counter (for rate limiting)"""
        if not self.enabled:
            return 0
        
        try:
            pipe = self.redis_client.pipeline()
            pipe.incr(key, amount)
            pipe.expire(key, ttl)
            result = pipe.execute()
            return result[0]
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return 0


# Global cache instance
cache = CacheManager()


def cached(ttl: int = 300, prefix: str = "cache"):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=600, prefix="exams")
        def get_exams(exam_type: str):
            return expensive_operation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._make_key(prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(prefix: str, *args, **kwargs):
    """Invalidate specific cache entry"""
    cache_key = cache._make_key(prefix, *args, **kwargs)
    cache.delete(cache_key)


def invalidate_pattern(pattern: str):
    """Invalidate all cache entries matching pattern"""
    cache.clear_pattern(f"{pattern}*")


# Rate limiting
class RateLimiter:
    """Simple rate limiter using Redis"""
    
    @staticmethod
    def check_rate_limit(
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if rate limit is exceeded
        
        Returns:
            (is_allowed, remaining_requests)
        """
        if not cache.enabled:
            return True, max_requests
        
        key = f"ratelimit:{identifier}"
        
        try:
            current = cache.increment(key, 1, window_seconds)
            remaining = max(0, max_requests - current)
            is_allowed = current <= max_requests
            
            return is_allowed, remaining
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, max_requests  # Allow on error
    
    @staticmethod
    def reset_rate_limit(identifier: str):
        """Reset rate limit for identifier"""
        key = f"ratelimit:{identifier}"
        cache.delete(key)


# Convenience functions
def cache_exam_data(exam_id: int, data: dict, ttl: int = 3600):
    """Cache exam data"""
    cache.set(f"exam:{exam_id}", data, ttl)


def get_cached_exam(exam_id: int) -> Optional[dict]:
    """Get cached exam data"""
    return cache.get(f"exam:{exam_id}")


def cache_user_recommendations(user_id: int, recommendations: dict, ttl: int = 600):
    """Cache user recommendations"""
    cache.set(f"recommendations:{user_id}", recommendations, ttl)


def get_cached_recommendations(user_id: int) -> Optional[dict]:
    """Get cached recommendations"""
    return cache.get(f"recommendations:{user_id}")


def invalidate_user_cache(user_id: int):
    """Invalidate all cache for a user"""
    invalidate_pattern(f"*:{user_id}")
