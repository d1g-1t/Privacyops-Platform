"""Unit tests for PASETO security module."""

from __future__ import annotations

import os
from uuid import uuid4

import pytest


# Set a deterministic SECRET_KEY before importing security module
os.environ.setdefault("PASETO_SECRET_KEY", "test-secret-key-for-unit-tests-only-32c")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from src.core.security import (  # noqa: E402
    create_paseto_token,
    decode_paseto_token,
    hash_password,
    verify_password,
)


class TestPasetoTokens:
    def test_create_and_decode_roundtrip(self):
        user_id = str(uuid4())
        tenant_id = str(uuid4())
        role = "dpo"

        token = create_paseto_token(user_id=user_id, tenant_id=tenant_id, role=role)
        assert isinstance(token, str)
        assert len(token) > 20

        payload = decode_paseto_token(token)
        assert payload["sub"] == user_id
        assert payload["tenant_id"] == tenant_id
        assert payload["role"] == role

    def test_decode_invalid_token_raises(self):
        with pytest.raises(Exception):
            decode_paseto_token("v4.local.garbage_token_data")


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "SecretПароль123!"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

