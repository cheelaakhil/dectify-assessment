"""
Tests for the cache abstraction layer.
"""
import pytest
from app.services.cache_service import MemoryCacheProvider, CacheProvider, get_cache, set_cache


@pytest.mark.asyncio
class TestMemoryCache:
    """Verify the in-memory cache honours TTL, delete, and clear."""

    async def test_set_and_get(self):
        cache = MemoryCacheProvider()
        await cache.set("key1", {"data": 42}, ttl=60)
        result = await cache.get("key1")
        assert result == {"data": 42}

    async def test_get_missing_key(self):
        cache = MemoryCacheProvider()
        result = await cache.get("nonexistent")
        assert result is None

    async def test_delete(self):
        cache = MemoryCacheProvider()
        await cache.set("key2", "value", ttl=60)
        await cache.delete("key2")
        result = await cache.get("key2")
        assert result is None

    async def test_clear(self):
        cache = MemoryCacheProvider()
        await cache.set("a", 1, ttl=60)
        await cache.set("b", 2, ttl=60)
        await cache.clear()
        assert await cache.get("a") is None
        assert await cache.get("b") is None

    async def test_ttl_expiration(self):
        cache = MemoryCacheProvider()
        await cache.set("expire", "soon", ttl=-1)  # already expired
        result = await cache.get("expire")
        assert result is None

    async def test_health_check(self):
        cache = MemoryCacheProvider()
        assert await cache.health_check() is True

    async def test_overwrite_value(self):
        cache = MemoryCacheProvider()
        await cache.set("key", "old", ttl=60)
        await cache.set("key", "new", ttl=60)
        assert await cache.get("key") == "new"

    async def test_stores_various_types(self):
        cache = MemoryCacheProvider()
        await cache.set("dict", {"a": 1}, ttl=60)
        await cache.set("list", [1, 2, 3], ttl=60)
        await cache.set("str", "hello", ttl=60)
        await cache.set("int", 42, ttl=60)
        assert await cache.get("dict") == {"a": 1}
        assert await cache.get("list") == [1, 2, 3]
        assert await cache.get("str") == "hello"
        assert await cache.get("int") == 42


@pytest.mark.asyncio
class TestCacheSwap:
    """Verify the set_cache() mechanism allows swapping providers (assessment requirement)."""

    async def test_default_provider_is_memory(self):
        import app.services.cache_service as mod
        mod._cache = None
        cache = get_cache()
        assert isinstance(cache, MemoryCacheProvider)
        mod._cache = None

    async def test_swap_provider(self):
        """Setting a custom provider should replace the default."""
        import app.services.cache_service as mod
        mod._cache = None

        class DummyCache(CacheProvider):
            async def get(self, key): return "dummy"
            async def set(self, key, value, ttl=3600): pass
            async def delete(self, key): pass
            async def clear(self): pass
            async def health_check(self): return True

        dummy = DummyCache()
        set_cache(dummy)
        assert get_cache() is dummy
        assert await get_cache().get("anything") == "dummy"
        mod._cache = None
