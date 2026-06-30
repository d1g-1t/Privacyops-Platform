from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_class=ORJSONResponse)
async def health_check(request: Request):
    return {
        "status": "ok",
        "service": "privacyops-152fz-control-tower",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready", response_class=ORJSONResponse)
async def readiness_check(request: Request):
    checks: dict[str, str] = {}
    try:
        redis: object = request.app.state.redis_cache
        await redis.set("__healthcheck__", "1", ttl=5)
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "unavailable"

    return {
        "status": "ok" if all(v == "ok" for v in checks.values()) else "degraded",
        "checks": checks,
        "timestamp": datetime.now(UTC).isoformat(),
    }
