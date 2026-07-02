from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.consent_capture import ConsentCapture
from src.domain.entities.consent_template import ConsentTemplate
from src.domain.repositories import BaseRepository


class ConsentRepository(BaseRepository[ConsentCapture]):
    @abstractmethod
    async def save_template(self, template: ConsentTemplate) -> ConsentTemplate: ...

    @abstractmethod
    async def get_template(self, template_id: UUID) -> ConsentTemplate | None: ...

    @abstractmethod
    async def list_templates(
        self, tenant_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> list[ConsentTemplate]: ...

    @abstractmethod
    async def find_expiring(
        self, tenant_id: UUID, *, before: datetime
    ) -> list[ConsentCapture]: ...

    @abstractmethod
    async def find_by_subject(
        self, tenant_id: UUID, subject_identifier: str
    ) -> list[ConsentCapture]: ...

    @abstractmethod
    async def withdraw(self, capture_id: UUID) -> ConsentCapture: ...
