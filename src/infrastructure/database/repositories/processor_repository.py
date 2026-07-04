from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.infrastructure.database.models import (
    ProcessorReviewModel,
    ProcessorVendorModel,
)
from src.infrastructure.database.repositories.base import SqlAlchemyBaseRepository


class SqlAlchemyProcessorRepository(SqlAlchemyBaseRepository[ProcessorVendorModel]):
    model_class = ProcessorVendorModel

    async def get_by_id(self, entity_id: UUID) -> ProcessorVendorModel | None:
        async with self._session_factory() as session:
            stmt = (
                select(ProcessorVendorModel)
                .options(selectinload(ProcessorVendorModel.reviews))
                .where(ProcessorVendorModel.id == str(entity_id))
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def save_review(self, review: ProcessorReviewModel) -> ProcessorReviewModel:
        async with self._session_factory() as session:
            session.add(review)
            await session.commit()
            await session.refresh(review)
            return review

    async def get_reviews(self, vendor_id: UUID) -> list[ProcessorReviewModel]:
        async with self._session_factory() as session:
            stmt = (
                select(ProcessorReviewModel)
                .where(ProcessorReviewModel.vendor_id == str(vendor_id))
                .order_by(ProcessorReviewModel.created_at.desc())
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def find_high_risk(self, tenant_id: UUID) -> list[ProcessorVendorModel]:
        async with self._session_factory() as session:
            high_risk_vendor_ids = (
                select(ProcessorReviewModel.vendor_id)
                .where(ProcessorReviewModel.risk_score >= 70)
                .distinct()
            )
            stmt = (
                select(ProcessorVendorModel)
                .where(
                    ProcessorVendorModel.tenant_id == str(tenant_id),
                    ProcessorVendorModel.id.in_(high_risk_vendor_ids),
                )
                .options(selectinload(ProcessorVendorModel.reviews))
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
