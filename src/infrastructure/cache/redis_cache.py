from __future__ import annotations

from typing import Any

import orjson
import redis.asyncio as aioredis
import structlog

logger = structlog.get_logger(__name__)

_DEFAULT_TTL = 300


class RedisCache:
    def __init__(self, url: str) -> None:
        self._url = url
        self._pool: aioredis.Redis | None = None

    async def _get_pool(self) -> aioredis.Redis:
        if self._pool is None:
            self._pool = aioredis.from_url(
                self._url,
                decode_responses=False,
                max_connections=20,
            )
        return self._pool

    def _key(self, namespace: str, key: str) -> str:
        return f"privacyops:{namespace}:{key}"

    async def get(self, namespace: str, key: str) -> Any | None:
        pool = await self._get_pool()
        raw = await pool.get(self._key(namespace, key))
        if raw is None:
            return None
        return orjson.loads(raw)

    async def set(
        self, namespace: str, key: str, value: Any, *, ttl: int = _DEFAULT_TTL
    ) -> None:
        pool = await self._get_pool()
        await pool.set(self._key(namespace, key), orjson.dumps(value), ex=ttl)

    async def delete(self, namespace: str, key: str) -> None:
        pool = await self._get_pool()
        await pool.delete(self._key(namespace, key))

    async def invalidate_namespace(self, namespace: str) -> int:
        pool = await self._get_pool()
        pattern = f"privacyops:{namespace}:*"
        count = 0
        async for key in pool.scan_iter(match=pattern, count=100):
            await pool.delete(key)
            count += 1
        logger.info("cache_invalidated", namespace=namespace, deleted=count)
        return count

    async def close(self) -> None:
        if self._pool:
            await self._pool.aclose()
            self._pool = None
