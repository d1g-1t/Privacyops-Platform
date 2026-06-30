from __future__ import annotations

import traceback
from typing import Any

import structlog
from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ComplianceViolationError,
    DomainError,
    DuplicateEntityError,
    EntityNotFoundError,
    InvalidStateTransitionError,
)

logger = structlog.get_logger(__name__)

_STATUS_MAP: dict[type[DomainError], int] = {
    EntityNotFoundError: status.HTTP_404_NOT_FOUND,
    DuplicateEntityError: status.HTTP_409_CONFLICT,
    InvalidStateTransitionError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    ComplianceViolationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        try:
            return await call_next(request)
        except DomainError as exc:
            http_status = _STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
            logger.warning(
                "domain_error",
                error_type=type(exc).__name__,
                detail=str(exc),
                path=request.url.path,
            )
            return ORJSONResponse(
                status_code=http_status,
                content={"detail": str(exc), "error_type": type(exc).__name__},
            )
        except Exception as exc:
            logger.error(
                "unhandled_error",
                error_type=type(exc).__name__,
                detail=str(exc),
                path=request.url.path,
                traceback=traceback.format_exc(),
            )
            return ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
            )
