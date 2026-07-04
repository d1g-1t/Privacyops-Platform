from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.processor_review import ProcessorReview
from src.domain.entities.processor_vendor import ProcessorVendor
from src.domain.repositories import BaseRepository


class ProcessorRepository(BaseRepository[ProcessorVendor]):
    @abstractmethod
    async def save_review(self, review: ProcessorReview) -> ProcessorReview: ...

    @abstractmethod
    async def get_reviews(self, vendor_id: UUID) -> list[ProcessorReview]: ...

    @abstractmethod
    async def find_high_risk(self, tenant_id: UUID) -> list[ProcessorVendor]: ...
