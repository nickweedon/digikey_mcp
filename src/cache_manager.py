"""
Cache manager for client-controlled pagination.

This module provides a caching infrastructure for handling large datasets
with client-controlled pagination. Based on the PartsBox MCP design pattern.
"""

import uuid
from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass
class CacheInfo:
    """Information about a cache entry."""

    valid: bool
    total_items: int | None = None
    age_seconds: int | None = None
    expires_in_seconds: int | None = None


@dataclass
class CacheEntry:
    """A cached dataset with TTL management."""

    data: list[dict[str, Any]]
    created_at: float = field(default_factory=time)
    last_accessed: float = field(default_factory=time)
    ttl: int = 300  # 5 minutes default

    def touch(self) -> None:
        """Update last accessed time."""
        self.last_accessed = time()

    @property
    def is_expired(self) -> bool:
        """Check if entry has exceeded TTL since last access."""
        return time() - self.last_accessed > self.ttl

    @property
    def age_seconds(self) -> int:
        """Seconds since cache was created."""
        return int(time() - self.created_at)

    @property
    def expires_in_seconds(self) -> int:
        """Seconds until cache expires (from last access)."""
        return max(0, int(self.ttl - (time() - self.last_accessed)))


class PaginationCache:
    """Manages cached datasets with client-controlled keys.

    This cache manager implements the following design principles:

    1. **Client-controlled**: Cache keys are returned to and provided by clients
    2. **Fresh by default**: Omitting the cache key fetches fresh data
    3. **Automatic cleanup**: Expired entries are removed lazily
    4. **Touch-based TTL**: TTL refreshes on access

    Cache keys follow the pattern: `dk_<8-char-hex>`
    Examples: dk_a7f3b2c1, dk_9e4d8f2a
    """

    def __init__(self, default_ttl: int = 300):
        """Initialize cache manager.

        Args:
            default_ttl: Default time-to-live in seconds (default: 300 = 5 minutes)
        """
        self._cache: dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl

    def create(self, data: list[dict[str, Any]]) -> str:
        """Store data and return a new cache key.

        Args:
            data: List of items to cache

        Returns:
            Unique cache key in format dk_<8-char-hex>
        """
        self._lazy_cleanup()
        key = f"dk_{uuid.uuid4().hex[:8]}"
        self._cache[key] = CacheEntry(data=data, ttl=self._default_ttl)
        return key

    def get(self, key: str) -> CacheEntry | None:
        """Retrieve cache entry, return None if missing/expired.

        Args:
            key: Cache key to retrieve

        Returns:
            CacheEntry if valid and not expired, None otherwise
        """
        self._lazy_cleanup()
        entry = self._cache.get(key)
        if entry and not entry.is_expired:
            entry.touch()  # Refresh TTL
            return entry
        # Clean up expired entry
        if key in self._cache:
            del self._cache[key]
        return None

    def get_info(self, key: str) -> CacheInfo:
        """Get information about a cache entry.

        Args:
            key: Cache key to inspect

        Returns:
            CacheInfo with validity and metadata
        """
        entry = self._cache.get(key)
        if not entry or entry.is_expired:
            return CacheInfo(valid=False)
        return CacheInfo(
            valid=True,
            total_items=len(entry.data),
            age_seconds=entry.age_seconds,
            expires_in_seconds=entry.expires_in_seconds,
        )

    def invalidate(self, key: str) -> bool:
        """Explicitly invalidate a cache entry.

        Args:
            key: Cache key to invalidate

        Returns:
            True if entry was found and removed, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear_all(self) -> int:
        """Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        return count

    def _lazy_cleanup(self) -> None:
        """Remove expired entries (called on each access)."""
        expired = [k for k, v in self._cache.items() if v.is_expired]
        for k in expired:
            del self._cache[k]


# Global cache instance
search_cache = PaginationCache(default_ttl=300)  # 5 minute TTL
