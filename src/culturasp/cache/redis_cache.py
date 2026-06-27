"""Redis cache wrapper.

Keys are namespaced (``culturasp:<kind>:<key>``). The wrapper degrades
gracefully: if Redis is unreachable, ``get`` returns ``None`` and ``set`` is a
no-op, so a missing cache never breaks a scrape (it just means a live fetch).
"""

from __future__ import annotations

from functools import lru_cache

import redis

from culturasp.core.config import get_settings
from culturasp.core.logging import get_logger

logger = get_logger(__name__)
_NAMESPACE = "culturasp"


class Cache:
    def __init__(self, client: redis.Redis | None, default_ttl: int) -> None:
        self._client = client
        self._default_ttl = default_ttl

    @staticmethod
    def _key(kind: str, key: str) -> str:
        return f"{_NAMESPACE}:{kind}:{key}"

    def get(self, kind: str, key: str) -> str | None:
        if self._client is None:
            return None
        try:
            value = self._client.get(self._key(kind, key))
            return value.decode("utf-8") if isinstance(value, bytes) else value
        except redis.RedisError as exc:  # pragma: no cover - network failure path
            logger.warning("cache_get_failed", error=str(exc))
            return None

    def set(self, kind: str, key: str, value: str, ttl: int | None = None) -> None:
        if self._client is None:
            return
        try:
            self._client.set(self._key(kind, key), value, ex=ttl or self._default_ttl)
        except redis.RedisError as exc:  # pragma: no cover - network failure path
            logger.warning("cache_set_failed", error=str(exc))


@lru_cache
def get_cache() -> Cache:
    settings = get_settings()
    client: redis.Redis | None
    try:
        connected = redis.from_url(settings.redis_url)
        connected.ping()
        client = connected
    except redis.RedisError as exc:  # pragma: no cover - allows running without Redis
        logger.warning("redis_unavailable", error=str(exc))
        client = None
    return Cache(client, settings.cache_ttl)
