from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select

from src.infrastructure.database.models import (
    ConsentCaptureModel,
    ConsentTemplateModel,
)
from src.infrastructure.database.repositories.base import SqlAlchemyBaseRepository


class SqlAlchemyConsentRepository(SqlAlchemyBaseRepository[ConsentCaptureModel]):
    model_class = ConsentCaptureModel

    async def save_template(self, template: ConsentTemplateModel) -> ConsentTemplateModel:
        async with self._session_factory() as session:
            session.add(template)
            await session.commit()
            await session.refresh(template)
            return template

    async def get_template(self, template_id: UUID) -> ConsentTemplateModel | None:
        async with self._session_factory() as session:
            return await session.get(ConsentTemplateModel, str(template_id))

    async def list_templates(
        self, tenant_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> list[ConsentTemplateModel]:
        async with self._session_factory() as session:
            stmt = (
                select(ConsentTemplateModel)
                .where(ConsentTemplateModel.tenant_id == str(tenant_id))
                .order_by(ConsentTemplateModel.name, ConsentTemplateModel.version.desc())
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def find_expiring(
        self, tenant_id: UUID, *, before: datetime
    ) -> list[ConsentCaptureModel]:
        async with self._session_factory() as session:
            stmt = (
                select(ConsentCaptureModel)
                .where(
                    ConsentCaptureModel.tenant_id == str(tenant_id),
                    ConsentCaptureModel.status == "active",
                    ConsentCaptureModel.captured_at <= before,
                )
                .order_by(ConsentCaptureModel.captured_at)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def find_by_subject(
        self, tenant_id: UUID, subject_identifier: str
    ) -> list[ConsentCaptureModel]:
        async with self._session_factory() as session:
            stmt = (
                select(ConsentCaptureModel)
                .where(
                    ConsentCaptureModel.tenant_id == str(tenant_id),
                    ConsentCaptureModel.subject_identifier == subject_identifier,
                )
                .order_by(ConsentCaptureModel.captured_at.desc())
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def withdraw(self, capture_id: UUID) -> ConsentCaptureModel:
        async with self._session_factory() as session:
            capture = await session.get(ConsentCaptureModel, str(capture_id))
            if not capture:
                raise ValueError(f"Consent capture {capture_id} not found")
            capture.status = "withdrawn"
            capture.withdrawn_at = datetime.now(UTC)
            await session.commit()
            await session.refresh(capture)
            return capture
