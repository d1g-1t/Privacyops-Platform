from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.entities.privacy_incident import PrivacyIncident
from src.domain.repositories import BaseRepository


class IncidentRepository(BaseRepository[PrivacyIncident]):
    @abstractmethod
    async def find_open(self, tenant_id: UUID) -> list[PrivacyIncident]: ...

    @abstractmethod
    async def find_by_severity(
        self, tenant_id: UUID, severity: str
    ) -> list[PrivacyIncident]: ...
