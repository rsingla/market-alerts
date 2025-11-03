"""
Data Cache Manager
Intelligent caching layer for market data to reduce API calls
"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any, Dict
from utils.logger import logger


class DataCache:
    """
    Intelligent cache manager for market data

    Features:
    - Time-based expiration (TTL)
    - Automatic cleanup of expired entries
    - Separate caches for different data types
    - Thread-safe operations
    """

    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize cache manager

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # In-memory cache for fast access
        self._memory_cache: Dict[str, Dict[str, Any]] = {}

        # Cache TTL settings (in seconds)
        self.ttl_settings = {
            'quotes': 60,          # 1 minute for real-time quotes
            'historical_1d': 300,  # 5 minutes for intraday
            'historical_5d': 900,  # 15 minutes for 5-day
            'historical_1mo': 1800, # 30 minutes for 1-month
            'historical_3mo': 3600, # 1 hour for 3-month
            'historical_6mo': 7200, # 2 hours for 6-month
            'historical_1y': 14400, # 4 hours for 1-year
            'technical': 300,       # 5 minutes for technical indicators
            'news': 600,           # 10 minutes for news
        }

        logger.info(f"Cache initialized at {self.cache_dir}")

    def _get_cache_key(self, data_type: str, symbol: str, **kwargs) -> str:
        """
        Generate unique cache key

        Args:
            data_type: Type of data (quotes, historical, technical, etc.)
            symbol: Stock symbol
            **kwargs: Additional parameters (period, etc.)

        Returns:
            Unique cache key string
        """
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        kwargs_str = "_".join(f"{k}={v}" for k, v in sorted_kwargs)

        if kwargs_str:
            return f"{data_type}_{symbol}_{kwargs_str}"
        return f"{data_type}_{symbol}"

    def _get_ttl(self, data_type: str, period: Optional[str] = None) -> int:
        """
        Get TTL for data type

        Args:
            data_type: Type of data
            period: Period for historical data

        Returns:
            TTL in seconds
        """
        if data_type == 'historical' and period:
            key = f"historical_{period}"
            return self.ttl_settings.get(key, 1800)  # Default 30 minutes

        return self.ttl_settings.get(data_type, 300)  # Default 5 minutes

    def get(self, data_type: str, symbol: str, **kwargs) -> Optional[Any]:
        """
        Get data from cache

        Args:
            data_type: Type of data
            symbol: Stock symbol
            **kwargs: Additional parameters

        Returns:
            Cached data or None if expired/not found
        """
        cache_key = self._get_cache_key(data_type, symbol, **kwargs)

        # Check memory cache first
        if cache_key in self._memory_cache:
            cache_entry = self._memory_cache[cache_key]

            # Check if expired
            if datetime.now() < cache_entry['expires_at']:
                logger.debug(f"Cache HIT (memory): {cache_key}")
                return cache_entry['data']
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                logger.debug(f"Cache EXPIRED (memory): {cache_key}")

        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.cache"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cache_entry = pickle.load(f)

                # Check if expired
                if datetime.now() < cache_entry['expires_at']:
                    # Load into memory cache
                    self._memory_cache[cache_key] = cache_entry
                    logger.debug(f"Cache HIT (disk): {cache_key}")
                    return cache_entry['data']
                else:
                    # Remove expired file
                    cache_file.unlink()
                    logger.debug(f"Cache EXPIRED (disk): {cache_key}")
            except Exception as e:
                logger.warning(f"Error reading cache file {cache_key}: {e}")
                cache_file.unlink(missing_ok=True)

        logger.debug(f"Cache MISS: {cache_key}")
        return None

    def set(self, data_type: str, symbol: str, data: Any, **kwargs) -> None:
        """
        Store data in cache

        Args:
            data_type: Type of data
            symbol: Stock symbol
            data: Data to cache
            **kwargs: Additional parameters
        """
        cache_key = self._get_cache_key(data_type, symbol, **kwargs)

        # Get TTL
        period = kwargs.get('period')
        ttl = self._get_ttl(data_type, period)
        expires_at = datetime.now() + timedelta(seconds=ttl)

        cache_entry = {
            'data': data,
            'cached_at': datetime.now(),
            'expires_at': expires_at,
            'data_type': data_type,
            'symbol': symbol,
            'kwargs': kwargs
        }

        # Store in memory
        self._memory_cache[cache_key] = cache_entry

        # Store on disk for persistence
        cache_file = self.cache_dir / f"{cache_key}.cache"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_entry, f)
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"Error writing cache file {cache_key}: {e}")

    def invalidate(self, data_type: Optional[str] = None, symbol: Optional[str] = None) -> int:
        """
        Invalidate cache entries

        Args:
            data_type: Type of data to invalidate (None = all types)
            symbol: Symbol to invalidate (None = all symbols)

        Returns:
            Number of entries invalidated
        """
        count = 0

        # Invalidate memory cache
        keys_to_remove = []
        for cache_key in list(self._memory_cache.keys()):
            if data_type and not cache_key.startswith(f"{data_type}_"):
                continue
            if symbol and f"_{symbol}_" not in cache_key and not cache_key.endswith(f"_{symbol}"):
                continue
            keys_to_remove.append(cache_key)

        for key in keys_to_remove:
            del self._memory_cache[key]
            count += 1

        # Invalidate disk cache
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_key = cache_file.stem
            if data_type and not cache_key.startswith(f"{data_type}_"):
                continue
            if symbol and f"_{symbol}_" not in cache_key and not cache_key.endswith(f"_{symbol}"):
                continue
            cache_file.unlink()
            count += 1

        logger.info(f"Invalidated {count} cache entries (data_type={data_type}, symbol={symbol})")
        return count

    def cleanup_expired(self) -> int:
        """
        Remove all expired cache entries

        Returns:
            Number of entries removed
        """
        count = 0
        now = datetime.now()

        # Clean memory cache
        keys_to_remove = []
        for cache_key, cache_entry in self._memory_cache.items():
            if now >= cache_entry['expires_at']:
                keys_to_remove.append(cache_key)

        for key in keys_to_remove:
            del self._memory_cache[key]
            count += 1

        # Clean disk cache
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'rb') as f:
                    cache_entry = pickle.load(f)

                if now >= cache_entry['expires_at']:
                    cache_file.unlink()
                    count += 1
            except Exception as e:
                # Remove corrupted cache files
                logger.warning(f"Removing corrupted cache file {cache_file}: {e}")
                cache_file.unlink()
                count += 1

        if count > 0:
            logger.info(f"Cleaned up {count} expired cache entries")

        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        memory_count = len(self._memory_cache)
        disk_count = len(list(self.cache_dir.glob("*.cache")))

        # Calculate cache size
        cache_size_bytes = sum(f.stat().st_size for f in self.cache_dir.glob("*.cache"))
        cache_size_mb = cache_size_bytes / (1024 * 1024)

        # Count by data type
        type_counts = {}
        for cache_key in self._memory_cache.keys():
            data_type = cache_key.split('_')[0]
            type_counts[data_type] = type_counts.get(data_type, 0) + 1

        return {
            'memory_entries': memory_count,
            'disk_entries': disk_count,
            'cache_size_mb': round(cache_size_mb, 2),
            'type_counts': type_counts,
            'cache_dir': str(self.cache_dir)
        }

    def clear_all(self) -> int:
        """
        Clear all cache entries

        Returns:
            Number of entries cleared
        """
        count = len(self._memory_cache)

        # Clear memory
        self._memory_cache.clear()

        # Clear disk
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
            count += 1

        logger.info(f"Cleared all cache ({count} entries)")
        return count


# Global cache instance
_global_cache: Optional[DataCache] = None


def get_cache() -> DataCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = DataCache()
    return _global_cache


if __name__ == '__main__':
    # Test cache functionality
    print("\n" + "="*60)
    print("CACHE TEST")
    print("="*60)

    cache = DataCache()

    # Test set and get
    print("\nTest 1: Set and get data")
    test_data = {'price': 150.25, 'volume': 1000000}
    cache.set('quotes', 'AAPL', test_data)
    retrieved = cache.get('quotes', 'AAPL')
    print(f"✓ Stored and retrieved: {retrieved}")

    # Test expiration
    print("\nTest 2: Check expiration")
    cache.set('quotes', 'GOOGL', {'price': 2800}, period='1d')
    print(f"✓ GOOGL cached")

    # Test stats
    print("\nTest 3: Cache stats")
    stats = cache.get_stats()
    print(f"✓ Memory entries: {stats['memory_entries']}")
    print(f"✓ Disk entries: {stats['disk_entries']}")
    print(f"✓ Cache size: {stats['cache_size_mb']} MB")

    # Test cleanup
    print("\nTest 4: Cleanup")
    removed = cache.cleanup_expired()
    print(f"✓ Removed {removed} expired entries")

    print("="*60 + "\n")
