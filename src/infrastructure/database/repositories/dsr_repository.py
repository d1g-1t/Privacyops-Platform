from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select

from src.infrastructure.database.models import DataSubjectRequestModel
from src.infrastructure.database.repositories.base import SqlAlchemyBaseRepository


class SqlAlchemyDSRRepository(SqlAlchemyBaseRepository[DataSubjectRequestModel]):
    model_class = DataSubjectRequestModel

    async def find_overdue(self, tenant_id: UUID) -> list[DataSubjectRequestModel]:
        async with self._session_factory() as session:
            now = datetime.now(UTC)
            stmt = (
                select(DataSubjectRequestModel)
                .where(
                    DataSubjectRequestModel.tenant_id == str(tenant_id),
                    DataSubjectRequestModel.status.notin_(["completed", "rejected"]),
                    DataSubjectRequestModel.due_at < now,
                )
                .order_by(DataSubjectRequestModel.due_at)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def find_near_overdue(
        self, tenant_id: UUID, *, days: int = 3
    ) -> list[DataSubjectRequestModel]:
        async with self._session_factory() as session:
            now = datetime.now(UTC)
            threshold = now + timedelta(days=days)
            stmt = (
                select(DataSubjectRequestModel)
                .where(
                    DataSubjectRequestModel.tenant_id == str(tenant_id),
                    DataSubjectRequestModel.status.notin_(["completed", "rejected"]),
                    DataSubjectRequestModel.due_at >= now,
                    DataSubjectRequestModel.due_at <= threshold,
                )
                .order_by(DataSubjectRequestModel.due_at)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def dashboard_stats(self, tenant_id: UUID) -> dict[str, int]:
        async with self._session_factory() as session:
            now = datetime.now(UTC)
            total = await session.execute(
                select(func.count()).select_from(DataSubjectRequestModel).where(
                    DataSubjectRequestModel.tenant_id == str(tenant_id)
                )
            )
            open_count = await session.execute(
                select(func.count()).select_from(DataSubjectRequestModel).where(
                    DataSubjectRequestModel.tenant_id == str(tenant_id),
                    DataSubjectRequestModel.status.notin_(["completed", "rejected"]),
                )
            )
            overdue = await session.execute(
                select(func.count()).select_from(DataSubjectRequestModel).where(
                    DataSubjectRequestModel.tenant_id == str(tenant_id),
                    DataSubjectRequestModel.status.notin_(["completed", "rejected"]),
                    DataSubjectRequestModel.due_at < now,
                )
            )
            completed = await session.execute(
                select(func.count()).select_from(DataSubjectRequestModel).where(
                    DataSubjectRequestModel.tenant_id == str(tenant_id),
                    DataSubjectRequestModel.status == "completed",
                )
            )
            return {
                "total": total.scalar_one(),
                "open": open_count.scalar_one(),
                "overdue": overdue.scalar_one(),
                "completed": completed.scalar_one(),
            }
