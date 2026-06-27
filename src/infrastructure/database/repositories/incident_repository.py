from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from src.infrastructure.database.models import PrivacyIncidentModel
from src.infrastructure.database.repositories.base import SqlAlchemyBaseRepository


class SqlAlchemyIncidentRepository(SqlAlchemyBaseRepository[PrivacyIncidentModel]):
    model_class = PrivacyIncidentModel

    async def find_open(self, tenant_id: UUID) -> list[PrivacyIncidentModel]:
        async with self._session_factory() as session:
            stmt = (
                select(PrivacyIncidentModel)
                .where(
                    PrivacyIncidentModel.tenant_id == str(tenant_id),
                    PrivacyIncidentModel.status.in_(["OPEN", "INVESTIGATING", "REMEDIATION"]),
                )
                .order_by(PrivacyIncidentModel.severity, PrivacyIncidentModel.detected_at)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def find_by_severity(
        self, tenant_id: UUID, severity: str
    ) -> list[PrivacyIncidentModel]:
        async with self._session_factory() as session:
            stmt = (
                select(PrivacyIncidentModel)
                .where(
                    PrivacyIncidentModel.tenant_id == str(tenant_id),
                    PrivacyIncidentModel.severity == severity,
                )
                .order_by(PrivacyIncidentModel.detected_at.desc())
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
