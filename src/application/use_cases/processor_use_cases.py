from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog

from src.application.dto.processor_dto import (
    CreateProcessorRequest,
    CreateProcessorReviewRequest,
    ProcessorResponse,
    ProcessorReviewResponse,
)
from src.domain.exceptions import EntityNotFoundError
from src.infrastructure.database.models import (
    AuditEventModel,
    ProcessorReviewModel,
    ProcessorVendorModel,
)
from src.infrastructure.database.repositories.audit_repository import SqlAlchemyAuditRepository
from src.infrastructure.database.repositories.processor_repository import (
    SqlAlchemyProcessorRepository,
)
from src.infrastructure.rules.engine import create_rule_engine

logger = structlog.get_logger(__name__)


class ProcessorUseCases:
    def __init__(
        self,
        repo: SqlAlchemyProcessorRepository,
        audit_repo: SqlAlchemyAuditRepository,
    ) -> None:
        self._repo = repo
        self._audit = audit_repo
        self._rule_engine = create_rule_engine()

    async def create_processor(
        self, tenant_id: UUID, request: CreateProcessorRequest, actor_id: UUID | None = None
    ) -> ProcessorResponse:
        model = ProcessorVendorModel(
            tenant_id=str(tenant_id),
            legal_name=request.legal_name,
            inn=request.inn,
            service_type=request.service_type,
            hosts_personal_data=request.hosts_personal_data,
            subprocessors_used=request.subprocessors_used,
            metadata_=request.metadata,
        )
        saved = await self._repo.save(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="processor",
                resource_id=str(saved.id),
                event_type="CREATED",
                payload=request.model_dump(),
            )
        )
        logger.info("processor_created", vendor_id=str(saved.id))
        return ProcessorResponse.model_validate(saved)

    async def get_processor(self, vendor_id: UUID) -> ProcessorResponse:
        model = await self._repo.get_by_id(vendor_id)
        if not model:
            raise EntityNotFoundError("Processor", str(vendor_id))
        return ProcessorResponse.model_validate(model)

    async def list_processors(
        self, tenant_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> list[ProcessorResponse]:
        models = await self._repo.list_by_tenant(tenant_id, offset=offset, limit=limit)
        return [ProcessorResponse.model_validate(m) for m in models]

    async def create_review(
        self, vendor_id: UUID, request: CreateProcessorReviewRequest, actor_id: UUID | None = None
    ) -> ProcessorReviewResponse:
        vendor = await self._repo.get_by_id(vendor_id)
        if not vendor:
            raise EntityNotFoundError("Processor", str(vendor_id))

        review = ProcessorReviewModel(
            vendor_id=str(vendor_id),
            review_status="COMPLETED",
            risk_score=request.risk_score,
            localization_supported=request.localization_supported,
            dpa_present=request.dpa_present,
            questionnaire_payload=request.questionnaire_payload,
            evidence_payload=request.evidence_payload,
            reviewer_id=str(actor_id) if actor_id else None,
            completed_at=datetime.now(UTC),
        )
        saved = await self._repo.save_review(review)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(vendor.tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="processor_review",
                resource_id=str(saved.id),
                event_type="CREATED",
                payload={"risk_score": str(request.risk_score)},
            )
        )
        logger.info("processor_review_created", review_id=str(saved.id), score=str(request.risk_score))
        return ProcessorReviewResponse.model_validate(saved)

    async def get_reviews(self, vendor_id: UUID) -> list[ProcessorReviewResponse]:
        models = await self._repo.get_reviews(vendor_id)
        return [ProcessorReviewResponse.model_validate(m) for m in models]

    async def approve_processor(self, vendor_id: UUID, actor_id: UUID | None = None) -> ProcessorResponse:
        model = await self._repo.get_by_id(vendor_id)
        if not model:
            raise EntityNotFoundError("Processor", str(vendor_id))

        model.status = "ACTIVE"
        updated = await self._repo.update(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(model.tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="processor",
                resource_id=str(vendor_id),
                event_type="APPROVED",
                payload={},
            )
        )
        return ProcessorResponse.model_validate(updated)

    async def reject_processor(
        self, vendor_id: UUID, reason: str, actor_id: UUID | None = None
    ) -> ProcessorResponse:
        model = await self._repo.get_by_id(vendor_id)
        if not model:
            raise EntityNotFoundError("Processor", str(vendor_id))

        model.status = "REJECTED"
        model.metadata_["rejection_reason"] = reason
        updated = await self._repo.update(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(model.tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="processor",
                resource_id=str(vendor_id),
                event_type="REJECTED",
                payload={"reason": reason},
            )
        )
        return ProcessorResponse.model_validate(updated)
