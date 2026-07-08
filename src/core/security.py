from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import bcrypt
import pyseto
from pyseto import Key


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _build_key(secret: str) -> Key:
    raw = secret.encode("utf-8")[:32].ljust(32, b"\x00")
    return Key.new(version=4, purpose="local", key=raw)


def create_access_token(
    *,
    secret: str,
    user_id: UUID,
    tenant_id: UUID,
    role: str,
    ttl_minutes: int = 30,
) -> str:
    key = _build_key(secret)
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "tid": str(tenant_id),
        "role": role,
        "iat": now.isoformat(),
        "exp": (now + timedelta(minutes=ttl_minutes)).isoformat(),
        "jti": secrets.token_hex(16),
    }
    import orjson

    token = pyseto.encode(key, orjson.dumps(payload))
    return token.decode("utf-8") if isinstance(token, bytes) else str(token)


def create_refresh_token(
    *,
    secret: str,
    user_id: UUID,
    tenant_id: UUID,
    ttl_days: int = 14,
) -> str:
    key = _build_key(secret)
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "tid": str(tenant_id),
        "type": "refresh",
        "iat": now.isoformat(),
        "exp": (now + timedelta(days=ttl_days)).isoformat(),
        "jti": secrets.token_hex(16),
    }
    import orjson

    token = pyseto.encode(key, orjson.dumps(payload))
    return token.decode("utf-8") if isinstance(token, bytes) else str(token)


def decode_token(*, secret: str, token: str) -> dict[str, Any]:
    key = _build_key(secret)
    decoded = pyseto.decode(key, token)
    import orjson

    payload: dict[str, Any] = orjson.loads(decoded.payload)
    exp = datetime.fromisoformat(payload["exp"])
    if exp < datetime.now(UTC):
        raise ValueError("Token expired")
    return payload


def create_paseto_token(
    *,
    user_id: str,
    tenant_id: str,
    role: str,
    ttl_minutes: int = 30,
) -> str:
    from src.core.config import settings

    return create_access_token(
        secret=settings.paseto_secret_key,
        user_id=UUID(user_id),
        tenant_id=UUID(tenant_id),
        role=role,
        ttl_minutes=ttl_minutes,
    )


def decode_paseto_token(token: str) -> dict[str, Any]:
    from src.core.config import settings

    payload = decode_token(secret=settings.paseto_secret_key, token=token)
    if "tid" in payload and "tenant_id" not in payload:
        payload["tenant_id"] = payload["tid"]
    return payload
