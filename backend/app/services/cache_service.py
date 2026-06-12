"""
Cache abstraction layer.

Phase 1: MemoryCacheProvider (in-process dict with TTL).
Phase 2 (bonus): RedisCacheProvider – drop-in replacement.
"""
import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------
class CacheProvider(ABC):
    """Interface that any cache backend must implement."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Return cached value or None if missing / expired."""
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Store a value with a TTL (seconds)."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove a key from the cache."""
        ...

    @abstractmethod
    async def clear(self) -> None:
        """Flush the entire cache."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the cache backend is operational."""
        ...


# ---------------------------------------------------------------------------
# In-memory implementation (Phase 1)
# ---------------------------------------------------------------------------
class MemoryCacheProvider(CacheProvider):
    """Simple dict-based cache with per-key TTL expiration."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}  # key → (value, expires_at)

    async def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            logger.debug("Cache MISS: %s", key)
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            logger.debug("Cache EXPIRED: %s", key)
            return None
        logger.debug("Cache HIT: %s", key)
        return value

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        self._store[key] = (value, time.time() + ttl)
        logger.debug("Cache SET: %s (ttl=%ds)", key, ttl)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def clear(self) -> None:
        self._store.clear()

    async def health_check(self) -> bool:
        return True


# ---------------------------------------------------------------------------
# Redis implementation (Phase 2 Bonus)
# ---------------------------------------------------------------------------
class RedisCacheProvider(CacheProvider):
    """Redis-based cache for multi-instance deployments."""

    def __init__(self, redis_url: str) -> None:
        import redis.asyncio as redis
        self.redis = redis.from_url(redis_url, decode_responses=True)
        logger.info("Initialized Redis cache at %s", redis_url)

    async def get(self, key: str) -> Any | None:
        value = await self.redis.get(key)
        if value is None:
            logger.debug("Redis Cache MISS: %s", key)
            return None
        logger.debug("Redis Cache HIT: %s", key)
        return json.loads(value)

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        await self.redis.set(key, json.dumps(value), ex=ttl)
        logger.debug("Redis Cache SET: %s (ttl=%ds)", key, ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def clear(self) -> None:
        await self.redis.flushdb()

    async def health_check(self) -> bool:
        try:
            return await self.redis.ping()
        except Exception as e:
            logger.error("Redis health check failed: %s", e)
            return False


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------
_cache: CacheProvider | None = None


def get_cache() -> CacheProvider:
    """Return the global cache instance (lazy-init MemoryCacheProvider)."""
    global _cache
    if _cache is None:
        _cache = MemoryCacheProvider()
    return _cache


def set_cache(provider: CacheProvider) -> None:
    """Swap the cache backend (useful for testing or switching to Redis)."""
    global _cache
    _cache = provider
