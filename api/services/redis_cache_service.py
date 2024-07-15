import aioredis
from aioredis.exceptions import RedisError

from interfaces.cache_interface import CacheInterface


class RedisCacheService(CacheInterface):
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)

    async def get(self, key: str):
        try:
            return await self.redis.get(key)
        except RedisError as e:
            print(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: str, expire: int = 3600):
        try:
            await self.redis.set(key, value, ex=expire)
        except RedisError as e:
            print(f"Redis set error: {e}")

    async def clear_cache(self) -> None:
        await self.redis.flushdb()
