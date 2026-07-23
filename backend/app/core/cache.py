"""Redis cache client helpers."""

import json
import logging
from typing import Any

from redis.asyncio import Redis

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class CacheClient:
    """Small JSON cache wrapper around Redis."""

    def __init__(self, redis: Redis, ttl_seconds: int) -> None:
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    async def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
        """Read a JSON value from cache."""
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            logger.exception("Redis cache read failed", extra={"request_id": "-"})
            return None

    async def set_json(self, key: str, value: dict[str, Any] | list[Any], ttl: int | None = None) -> None:
        """Write a JSON value to cache."""
        try:
            await self.redis.set(key, json.dumps(value), ex=ttl or self.ttl_seconds)
        except Exception:
            logger.exception("Redis cache write failed", extra={"request_id": "-"})


_redis: Redis | None = None


def get_redis(settings: Settings | None = None) -> Redis:
    """Return a shared async Redis connection."""
    global _redis
    if _redis is None:
        settings = settings or get_settings()
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def get_cache_client(settings: Settings | None = None) -> CacheClient:
    """Return a cache client with configured TTL."""
    settings = settings or get_settings()
    return CacheClient(get_redis(settings), settings.cache_ttl_seconds)

