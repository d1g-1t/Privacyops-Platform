from __future__ import annotations

from abc import abstractmethod
from typing import Any
from uuid import UUID

from src.domain.entities.evidence_item import EvidenceItem
from src.domain.repositories import BaseRepository


class EvidenceRepository(BaseRepository[EvidenceItem]):
    @abstractmethod
    async def find_by_resource(
        self, resource_type: str, resource_id: UUID
    ) -> list[EvidenceItem]: ...

    @abstractmethod
    async def export_package(
        self, resource_type: str, resource_id: UUID
    ) -> dict[str, Any]: ...
