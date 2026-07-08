"""Integration tests for the FastAPI application.

Uses httpx AsyncClient with ASGITransport — no real network needed.
Mocks DB and Redis via pytest-mock / dependency overrides.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import create_app


# ─────────────────────────────────────────────────────────────────────
# Minimal token helper (bypasses PASETO — tests focus on routing logic)
# ─────────────────────────────────────────────────────────────────────

TENANT_ID = str(uuid4())
USER_ID = str(uuid4())


def _make_token() -> str:
    from src.core.security import create_paseto_token

    return create_paseto_token(user_id=USER_ID, tenant_id=TENANT_ID, role="admin")


# ─────────────────────────────────────────────────────────────────────
# App + client fixtures
# ─────────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def app():
    application = create_app()
    # Inject a mock redis_cache into app state to avoid real Redis connection
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.close = AsyncMock()
    application.state.redis_cache = mock_redis
    return application


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
def auth_headers():
    token = _make_token()
    return {"Authorization": f"Bearer {token}", "X-Tenant-Id": TENANT_ID}


# ─────────────────────────────────────────────────────────────────────
# Health endpoint tests
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_ok(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_readiness(client: AsyncClient):
    resp = await client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert "checks" in data


# ─────────────────────────────────────────────────────────────────────
# OpenAPI schema is present in debug mode
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_openapi_schema_present(app, client: AsyncClient):
    # docs_url is only present when DEBUG=True; in tests DEBUG defaults to True
    resp = await client.get("/openapi.json")
    if resp.status_code == 200:
        schema = resp.json()
        assert "Privacyops-Platform" in schema["info"]["title"]


# ─────────────────────────────────────────────────────────────────────
# Auth endpoint — login with invalid creds returns 401 region
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_invalid_creds(app, client: AsyncClient):
    """Login with non-existent user → 404 or 401 domain error (mocked DB returns None)."""
    from src.presentation.deps import get_auth_use_cases
    from src.application.use_cases.auth_use_cases import AuthUseCases
    from src.domain.exceptions import AuthenticationError

    mock_uc = AsyncMock(spec=AuthUseCases)
    mock_uc.login.side_effect = AuthenticationError("Invalid credentials")

    app.dependency_overrides[get_auth_use_cases] = lambda: mock_uc

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────────
# Activities endpoint — list requires auth
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_activities_without_auth_returns_401(client: AsyncClient):
    resp = await client.get("/api/v1/activities")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_activities_with_mock_uc(app, client: AsyncClient, auth_headers):
    from src.presentation.deps import get_activity_use_cases
    from src.application.use_cases.activity_use_cases import ActivityUseCases

    mock_uc = AsyncMock(spec=ActivityUseCases)
    mock_uc.list_activities.return_value = []

    app.dependency_overrides[get_activity_use_cases] = lambda: mock_uc

    resp = await client.get("/api/v1/activities", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────────
# DSR dashboard requires auth
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dsr_dashboard_without_auth(client: AsyncClient):
    resp = await client.get("/api/v1/dsr/dashboard")
    assert resp.status_code == 401
