"""
Simple Caching System
Reduces API calls by caching results
"""

from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
from config import settings
from utils.logger import logger


class SimpleCache:
    """Simple in-memory cache with expiration"""

    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/not found
        """
        if key not in self._cache:
            return None

        # Check expiration
        if key in self._expiry and datetime.now() > self._expiry[key]:
            logger.debug(f"Cache expired for key: {key}")
            del self._cache[key]
            del self._expiry[key]
            return None

        logger.debug(f"Cache hit for key: {key}")
        return self._cache[key]

    def set(self, key: str, value: Any, duration: Optional[int] = None):
        """
        Set value in cache with expiration

        Args:
            key: Cache key
            value: Value to cache
            duration: Expiration duration in seconds (uses CACHE_DURATION if None)
        """
        if duration is None:
            duration = settings.CACHE_DURATION

        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=duration)
        logger.debug(f"Cached key: {key} (expires in {duration}s)")

    def clear(self, key: Optional[str] = None):
        """
        Clear cache

        Args:
            key: Specific key to clear (clears all if None)
        """
        if key:
            if key in self._cache:
                del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            logger.debug(f"Cleared cache for key: {key}")
        else:
            self._cache.clear()
            self._expiry.clear()
            logger.debug("Cleared entire cache")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        now = datetime.now()
        active_keys = [k for k, exp in self._expiry.items() if exp > now]

        return {
            'total_keys': len(self._cache),
            'active_keys': len(active_keys),
            'expired_keys': len(self._cache) - len(active_keys)
        }


# Global cache instance
_cache = SimpleCache()


def cached(duration: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results

    Args:
        duration: Cache duration in seconds
        key_prefix: Prefix for cache key

    Usage:
        @cached(duration=300, key_prefix="quotes")
        def get_stock_quote(symbol):
            return fetch_quote(symbol)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(filter(None, key_parts))

            # Try to get from cache
            result = _cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}, executing...")
            result = func(*args, **kwargs)

            if result is not None:
                _cache.set(cache_key, result, duration)

            return result

        return wrapper
    return decorator


def get_cache() -> SimpleCache:
    """Get global cache instance"""
    return _cache


def clear_cache(pattern: Optional[str] = None):
    """
    Clear cache entries

    Args:
        pattern: Clear keys matching pattern (clears all if None)
    """
    if pattern is None:
        _cache.clear()
    else:
        # Clear keys matching pattern
        keys_to_clear = [k for k in _cache._cache.keys() if pattern in k]
        for key in keys_to_clear:
            _cache.clear(key)
        logger.info(f"Cleared {len(keys_to_clear)} cache entries matching '{pattern}'")


if __name__ == '__main__':
    # Test caching
    import time

    print("\n" + "="*60)
    print("CACHE TEST")
    print("="*60)

    cache = SimpleCache()

    # Test basic get/set
    print("\nTesting basic cache operations...")
    cache.set("test_key", {"value": 123}, duration=2)
    result = cache.get("test_key")
    print(f"✓ Cached value: {result}")

    # Test expiration
    print("\nWaiting for cache to expire (2 seconds)...")
    time.sleep(2.5)
    result = cache.get("test_key")
    print(f"✓ After expiration: {result}")

    # Test decorator
    print("\nTesting cache decorator...")

    call_count = 0

    @cached(duration=5, key_prefix="test")
    def expensive_function(x):
        global call_count
        call_count += 1
        print(f"  Executing expensive function (call #{call_count})")
        return x * 2

    result1 = expensive_function(5)
    print(f"✓ First call result: {result1}")

    result2 = expensive_function(5)
    print(f"✓ Second call result: {result2} (should be cached)")

    result3 = expensive_function(10)
    print(f"✓ Different arg result: {result3} (new cache entry)")

    # Test stats
    print("\nCache statistics:")
    stats = _cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("="*60 + "\n")
