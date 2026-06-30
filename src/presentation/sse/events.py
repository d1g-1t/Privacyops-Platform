from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, AsyncGenerator
from uuid import UUID

import structlog

logger = structlog.get_logger(__name__)

_subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = defaultdict(list)


async def subscribe(tenant_id: UUID) -> AsyncGenerator[dict[str, Any], None]:
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    key = str(tenant_id)
    _subscribers[key].append(queue)
    try:
        while True:
            event = await queue.get()
            yield event
    finally:
        _subscribers[key].remove(queue)


async def publish(tenant_id: UUID, event_type: str, payload: dict[str, Any]) -> None:
    key = str(tenant_id)
    for q in _subscribers.get(key, []):
        await q.put({"event": event_type, "data": payload})
    logger.debug("sse_published", tenant_id=key, event=event_type)
