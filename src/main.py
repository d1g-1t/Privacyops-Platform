from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_client import make_asgi_app

from src.core.config import settings
from src.core.logging import setup_logging
from src.core.telemetry import setup_telemetry
from src.infrastructure.cache.redis_cache import RedisCache
from src.presentation.api.v1.router import api_v1_router
from src.presentation.middleware.audit import AuditMiddleware
from src.presentation.middleware.error_handler import ErrorHandlerMiddleware
from src.presentation.middleware.tenant import TenantMiddleware

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info(
        "starting",
        service="privacyops-152fz-control-tower",
        debug=getattr(settings, "app_env", "dev"),
    )

    if settings.otel_exporter_otlp_endpoint:
        setup_telemetry(app)

    redis = RedisCache(settings.redis_url)
    app.state.redis_cache = redis

    yield

    await redis.close()
    logger.info("shutdown_complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="PrivacyOps 152-FZ Control Tower",
        description="Enterprise privacy governance platform for Russian 152-FZ compliance",
        version="0.1.0",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(TenantMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router)

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    return app


app = create_app()
