from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from src.infrastructure.database.models import AuditEventModel
from src.infrastructure.database.repositories.base import SqlAlchemyBaseRepository


class SqlAlchemyAuditRepository(SqlAlchemyBaseRepository[AuditEventModel]):
    model_class = AuditEventModel

    async def find_by_resource(
        self, resource_type: str, resource_id: UUID, *, limit: int = 100
    ) -> list[AuditEventModel]:
        async with self._session_factory() as session:
            stmt = (
                select(AuditEventModel)
                .where(
                    AuditEventModel.resource_type == resource_type,
                    AuditEventModel.resource_id == str(resource_id),
                )
                .order_by(AuditEventModel.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def record(self, event: AuditEventModel) -> AuditEventModel:
        async with self._session_factory() as session:
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event
