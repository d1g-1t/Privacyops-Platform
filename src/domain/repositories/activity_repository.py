from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.data_processing_activity import DataProcessingActivity
from src.domain.repositories import BaseRepository


class ActivityRepository(BaseRepository[DataProcessingActivity]):
    @abstractmethod
    async def find_by_system(
        self, tenant_id: UUID, system_name: str
    ) -> list[DataProcessingActivity]: ...

    @abstractmethod
    async def find_without_legal_basis(
        self, tenant_id: UUID
    ) -> list[DataProcessingActivity]: ...

    @abstractmethod
    async def find_localization_gaps(
        self, tenant_id: UUID
    ) -> list[DataProcessingActivity]: ...
