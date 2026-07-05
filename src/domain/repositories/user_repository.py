from __future__ import annotations

from abc import abstractmethod
from uuid import UUID

from src.domain.repositories import BaseRepository


class UserRepository(BaseRepository["Any"]):
    @abstractmethod
    async def get_by_email(self, email: str) -> "Any | None": ...

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> "Any | None": ...
