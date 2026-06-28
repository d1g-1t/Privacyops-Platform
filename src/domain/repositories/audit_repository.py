from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.audit_event import AuditEvent
from src.domain.repositories import BaseRepository


class AuditRepository(BaseRepository[AuditEvent]):
    @abstractmethod
    async def find_by_resource(
        self, resource_type: str, resource_id: UUID, *, limit: int = 100
    ) -> list[AuditEvent]: ...

    @abstractmethod
    async def record(self, event: AuditEvent) -> AuditEvent: ...
