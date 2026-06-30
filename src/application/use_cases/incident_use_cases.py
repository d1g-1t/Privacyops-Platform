from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog

from src.application.dto.incident_dto import (
    CreateIncidentRequest,
    IncidentResponse,
    UpdateIncidentRequest,
)
from src.domain.exceptions import EntityNotFoundError, InvalidStateTransitionError
from src.infrastructure.database.models import AuditEventModel, PrivacyIncidentModel
from src.infrastructure.database.repositories.audit_repository import SqlAlchemyAuditRepository
from src.infrastructure.database.repositories.incident_repository import (
    SqlAlchemyIncidentRepository,
)

logger = structlog.get_logger(__name__)


class IncidentUseCases:
    def __init__(
        self,
        repo: SqlAlchemyIncidentRepository,
        audit_repo: SqlAlchemyAuditRepository,
    ) -> None:
        self._repo = repo
        self._audit = audit_repo

    async def create_incident(
        self, tenant_id: UUID, request: CreateIncidentRequest, actor_id: UUID | None = None
    ) -> IncidentResponse:
        model = PrivacyIncidentModel(
            tenant_id=str(tenant_id),
            title=request.title,
            description=request.description,
            severity=request.severity,
            detected_at=request.detected_at or datetime.now(UTC),
            category=request.category,
            status="DETECTED",
            metadata_=request.metadata or {},
        )
        saved = await self._repo.save(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="incident",
                resource_id=str(saved.id),
                event_type="CREATED",
                payload={"severity": request.severity, "title": request.title},
            )
        )
        logger.info("incident_created", incident_id=str(saved.id), severity=request.severity)
        return IncidentResponse.model_validate(saved)

    async def get_incident(self, incident_id: UUID) -> IncidentResponse:
        model = await self._repo.get_by_id(incident_id)
        if not model:
            raise EntityNotFoundError("Incident", str(incident_id))
        return IncidentResponse.model_validate(model)

    async def list_incidents(
        self, tenant_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> list[IncidentResponse]:
        models = await self._repo.list_by_tenant(tenant_id, offset=offset, limit=limit)
        return [IncidentResponse.model_validate(m) for m in models]

    async def update_incident(
        self, incident_id: UUID, request: UpdateIncidentRequest, actor_id: UUID | None = None
    ) -> IncidentResponse:
        model = await self._repo.get_by_id(incident_id)
        if not model:
            raise EntityNotFoundError("Incident", str(incident_id))

        if request.status:
            valid_transitions: dict[str, set[str]] = {
                "DETECTED": {"INVESTIGATING", "CONTAINED"},
                "INVESTIGATING": {"CONTAINED", "REMEDIATED"},
                "CONTAINED": {"REMEDIATED"},
                "REMEDIATED": {"CLOSED"},
            }
            current = model.status
            if request.status not in valid_transitions.get(current, set()):
                raise InvalidStateTransitionError("Incident", current, request.status)
            model.status = request.status
            if request.status == "CLOSED":
                model.closed_at = datetime.now(UTC)

        if request.severity is not None:
            model.severity = request.severity
        if request.resolution is not None:
            model.metadata_["resolution"] = request.resolution
        if request.roskomnadzor_notified is not None:
            model.roskomnadzor_notified = request.roskomnadzor_notified
            if request.roskomnadzor_notified:
                model.metadata_["rkn_notified_at"] = datetime.now(UTC).isoformat()

        updated = await self._repo.update(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(model.tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="incident",
                resource_id=str(incident_id),
                event_type="UPDATED",
                payload=request.model_dump(exclude_unset=True),
            )
        )
        return IncidentResponse.model_validate(updated)

    async def get_rkn_report(self, tenant_id: UUID) -> dict[str, Any]:
        """Generate aggregated Roskomnadzor notification report."""
        incidents = await self._repo.list_by_tenant(tenant_id, offset=0, limit=1000)
        critical = [i for i in incidents if i.severity in ("CRITICAL", "HIGH")]
        notifiable = [
            i
            for i in critical
            if not getattr(i, "roskomnadzor_notified", False)
        ]
        return {
            "total_incidents": len(incidents),
            "critical_high": len(critical),
            "pending_rkn_notification": len(notifiable),
            "incidents": [
                {
                    "id": str(i.id),
                    "title": i.title,
                    "severity": i.severity,
                    "detected_at": i.detected_at.isoformat() if i.detected_at else None,
                }
                for i in notifiable
            ],
        }
