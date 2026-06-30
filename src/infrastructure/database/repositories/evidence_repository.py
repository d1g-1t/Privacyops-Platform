from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select

from src.infrastructure.database.models import EvidenceItemModel
from src.infrastructure.database.repositories.base import SqlAlchemyBaseRepository


class SqlAlchemyEvidenceRepository(SqlAlchemyBaseRepository[EvidenceItemModel]):
    model_class = EvidenceItemModel

    async def find_by_resource(
        self, resource_type: str, resource_id: UUID
    ) -> list[EvidenceItemModel]:
        async with self._session_factory() as session:
            stmt = (
                select(EvidenceItemModel)
                .where(
                    EvidenceItemModel.resource_type == resource_type,
                    EvidenceItemModel.resource_id == str(resource_id),
                )
                .order_by(EvidenceItemModel.created_at.desc())
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def export_package(
        self, resource_type: str, resource_id: UUID
    ) -> dict[str, Any]:
        items = await self.find_by_resource(resource_type, resource_id)
        return {
            "resource_type": resource_type,
            "resource_id": str(resource_id),
            "items_count": len(items),
            "items": [
                {
                    "id": str(item.id),
                    "title": item.title,
                    "file_path": item.file_path,
                    "payload": item.payload,
                    "created_at": str(item.created_at),
                }
                for item in items
            ],
        }
