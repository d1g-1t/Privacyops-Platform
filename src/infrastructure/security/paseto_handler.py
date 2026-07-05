from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import Settings, get_settings
from src.core.security import decode_token

_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    try:
        payload = decode_token(secret=settings.paseto_secret_key, token=credentials.credentials)
        if "tid" in payload and "tenant_id" not in payload:
            payload["tenant_id"] = payload["tid"]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        ) from exc
    return payload


get_current_user_payload = get_current_user


async def get_current_tenant_id(
    user: dict[str, Any] = Depends(get_current_user),
) -> UUID:
    return UUID(user["tid"])

