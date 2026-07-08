from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog

from src.application.dto.dsr_dto import (
    AssignDSRRequest,
    CompleteDSRRequest,
    CreateDSRRequest,
    DSRDashboardResponse,
    DSRResponse,
    RespondDSRRequest,
)
from src.domain.exceptions import EntityNotFoundError, InvalidStateTransitionError
from src.infrastructure.database.models import AuditEventModel, DataSubjectRequestModel
from src.infrastructure.database.repositories.audit_repository import SqlAlchemyAuditRepository
from src.infrastructure.database.repositories.dsr_repository import SqlAlchemyDSRRepository

logger = structlog.get_logger(__name__)


class DSRUseCases:
    def __init__(
        self,
        repo: SqlAlchemyDSRRepository,
        audit_repo: SqlAlchemyAuditRepository,
    ) -> None:
        self._repo = repo
        self._audit = audit_repo

    async def create_dsr(
        self, tenant_id: UUID, request: CreateDSRRequest, actor_id: UUID | None = None
    ) -> DSRResponse:
        model = DataSubjectRequestModel(
            tenant_id=str(tenant_id),
            request_type=request.request_type,
            subject_identifier=request.subject_identifier,
            due_at=request.due_at,
            status="open",
        )
        saved = await self._repo.save(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="dsr",
                resource_id=str(saved.id),
                event_type="CREATED",
                payload=request.model_dump(mode="json"),
            )
        )
        logger.info("dsr_created", dsr_id=str(saved.id), type=request.request_type)
        return DSRResponse.model_validate(saved)

    async def get_dsr(self, dsr_id: UUID) -> DSRResponse:
        model = await self._repo.get_by_id(dsr_id)
        if not model:
            raise EntityNotFoundError("DSR", str(dsr_id))
        return DSRResponse.model_validate(model)

    async def list_dsrs(
        self, tenant_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> list[DSRResponse]:
        models = await self._repo.list_by_tenant(tenant_id, offset=offset, limit=limit)
        return [DSRResponse.model_validate(m) for m in models]

    async def assign_dsr(
        self, dsr_id: UUID, request: AssignDSRRequest, actor_id: UUID | None = None
    ) -> DSRResponse:
        model = await self._repo.get_by_id(dsr_id)
        if not model:
            raise EntityNotFoundError("DSR", str(dsr_id))
        if model.status not in ("open", "assigned"):
            raise InvalidStateTransitionError("DSR", model.status, "assigned")

        model.assigned_user_id = str(request.assigned_user_id)
        model.status = "assigned"
        updated = await self._repo.update(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(model.tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="dsr",
                resource_id=str(dsr_id),
                event_type="ASSIGNED",
                payload={"assigned_to": str(request.assigned_user_id)},
            )
        )
        return DSRResponse.model_validate(updated)

    async def respond_dsr(
        self, dsr_id: UUID, request: RespondDSRRequest, actor_id: UUID | None = None
    ) -> DSRResponse:
        model = await self._repo.get_by_id(dsr_id)
        if not model:
            raise EntityNotFoundError("DSR", str(dsr_id))

        model.response_payload = request.response_payload
        model.status = "responded"
        updated = await self._repo.update(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(model.tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="dsr",
                resource_id=str(dsr_id),
                event_type="RESPONDED",
                payload={},
            )
        )
        return DSRResponse.model_validate(updated)

    async def complete_dsr(
        self, dsr_id: UUID, request: CompleteDSRRequest, actor_id: UUID | None = None
    ) -> DSRResponse:
        model = await self._repo.get_by_id(dsr_id)
        if not model:
            raise EntityNotFoundError("DSR", str(dsr_id))

        model.status = "completed"
        model.completed_at = datetime.now(UTC)
        model.evidence_payload = request.evidence_payload
        updated = await self._repo.update(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(model.tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="dsr",
                resource_id=str(dsr_id),
                event_type="COMPLETED",
                payload={"completed_at": model.completed_at.isoformat()},
            )
        )
        return DSRResponse.model_validate(updated)

    async def dashboard(self, tenant_id: UUID) -> DSRDashboardResponse:
        stats = await self._repo.dashboard_stats(tenant_id)
        return DSRDashboardResponse(**stats)
