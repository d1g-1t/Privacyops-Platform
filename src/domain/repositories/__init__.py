"""Domain repository interfaces (ports) — no infrastructure leaks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base for all repositories in the domain layer."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None: ...

    @abstractmethod
    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        offset: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> list[T]: ...

    @abstractmethod
    async def count_by_tenant(
        self,
        tenant_id: UUID,
        *,
        filters: dict[str, Any] | None = None,
    ) -> int: ...

    @abstractmethod
    async def save(self, entity: T) -> T: ...

    @abstractmethod
    async def update(self, entity: T) -> T: ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> None: ...
