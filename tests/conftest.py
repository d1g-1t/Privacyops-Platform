"""Shared test fixtures."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


# ── Event loop ─────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Deterministic UUIDs for tests ──────────────────────────────────────

@pytest.fixture
def tenant_id():
    return uuid4()


@pytest.fixture
def user_id():
    return uuid4()


# ── Timestamps ─────────────────────────────────────────────────────────

@pytest.fixture
def now():
    return datetime.now(UTC)
