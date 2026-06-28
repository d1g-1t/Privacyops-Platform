from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.data_subject_request import DataSubjectRequest
from src.domain.repositories import BaseRepository


class DSRRepository(BaseRepository[DataSubjectRequest]):
    @abstractmethod
    async def find_overdue(self, tenant_id: UUID) -> list[DataSubjectRequest]: ...

    @abstractmethod
    async def find_near_overdue(
        self, tenant_id: UUID, *, days: int = 3
    ) -> list[DataSubjectRequest]: ...

    @abstractmethod
    async def dashboard_stats(self, tenant_id: UUID) -> dict[str, int]: ...
