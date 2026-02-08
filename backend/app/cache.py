import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

import redis.asyncio as redis

from .config import settings


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal and datetime types"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class RedisCache:
    """
    Redis cache helper for storing and retrieving data.
    Uses async redis client for better performance.
    """

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis server"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)

    async def disconnect(self):
        """Disconnect from Redis server"""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache by key.
        Returns None if key doesn't exist.
        """
        if not self.redis_client:
            await self.connect()

        value = await self.redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with optional TTL (time to live).
        TTL in seconds, defaults to settings.cache_ttl.
        """
        if not self.redis_client:
            await self.connect()

        ttl = ttl or settings.cache_ttl

        # Serialize value to JSON if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value, cls=CustomJSONEncoder)

        return await self.redis_client.setex(key, ttl, value)

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            await self.connect()

        return await self.redis_client.delete(key) > 0

    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        Example: clear_pattern("products:*") deletes all product cache.
        """
        if not self.redis_client:
            await self.connect()

        keys = await self.redis_client.keys(pattern)
        if keys:
            return await self.redis_client.delete(*keys)
        return 0


# Global cache instance
cache = RedisCac
