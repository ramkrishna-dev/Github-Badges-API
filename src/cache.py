import redis.asyncio as redis
from typing import Optional
from .config import settings

_cache = {}

class Cache:
    def __init__(self):
        self.redis = None
        if settings.REDIS_URL:
            self.redis = redis.from_url(settings.REDIS_URL)

    async def get(self, key: str) -> Optional[str]:
        if self.redis:
            return await self.redis.get(key)
        return _cache.get(key)

    async def set(self, key: str, value: str, ttl: int = 300):
        if self.redis:
            await self.redis.setex(key, ttl, value)
        else:
            _cache[key] = value
            # Simple ttl, but not implemented for in-memory

cache = Cache()

async def cache_get(key: str) -> Optional[str]:
    return await cache.get(key)

async def cache_set(key: str, value: str, ttl: int = 300):
    await cache.set(key, value, ttl)