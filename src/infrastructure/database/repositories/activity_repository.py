from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.infrastructure.database.models import (
    DataProcessingActivityModel,
    LegalBasisRecordModel,
)
from src.infrastructure.database.repositories.base import SqlAlchemyBaseRepository


class SqlAlchemyActivityRepository(SqlAlchemyBaseRepository[DataProcessingActivityModel]):
    model_class = DataProcessingActivityModel

    async def get_by_id(self, entity_id: UUID) -> DataProcessingActivityModel | None:
        async with self._session_factory() as session:
            stmt = (
                select(DataProcessingActivityModel)
                .options(
                    selectinload(DataProcessingActivityModel.legal_bases),
                    selectinload(DataProcessingActivityModel.transfers),
                    selectinload(DataProcessingActivityModel.localization_assessments),
                )
                .where(DataProcessingActivityModel.id == str(entity_id))
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def find_by_system(
        self, tenant_id: UUID, system_name: str
    ) -> list[DataProcessingActivityModel]:
        async with self._session_factory() as session:
            stmt = (
                select(DataProcessingActivityModel)
                .where(
                    DataProcessingActivityModel.tenant_id == str(tenant_id),
                    DataProcessingActivityModel.system_name == system_name,
                )
                .options(selectinload(DataProcessingActivityModel.legal_bases))
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def find_without_legal_basis(
        self, tenant_id: UUID
    ) -> list[DataProcessingActivityModel]:
        async with self._session_factory() as session:
            subq = select(LegalBasisRecordModel.activity_id).where(
                LegalBasisRecordModel.active.is_(True)
            )
            stmt = (
                select(DataProcessingActivityModel)
                .where(
                    DataProcessingActivityModel.tenant_id == str(tenant_id),
                    DataProcessingActivityModel.status == "active",
                    DataProcessingActivityModel.id.notin_(subq),
                )
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def find_localization_gaps(
        self, tenant_id: UUID
    ) -> list[DataProcessingActivityModel]:
        async with self._session_factory() as session:
            stmt = (
                select(DataProcessingActivityModel)
                .where(
                    DataProcessingActivityModel.tenant_id == str(tenant_id),
                    DataProcessingActivityModel.localization_status.in_(
                        ["unknown", "non_compliant"]
                    ),
                )
                .options(selectinload(DataProcessingActivityModel.localization_assessments))
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
