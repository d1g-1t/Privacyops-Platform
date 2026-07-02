from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog

from src.application.dto.activity_dto import (
    ActivityResponse,
    CreateActivityRequest,
    CreateLegalBasisRequest,
    CreateLocalizationAssessmentRequest,
    CreateTransferRequest,
    UpdateActivityRequest,
)
from src.domain.exceptions import EntityNotFoundError
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.database.models import (
    AuditEventModel,
    DataProcessingActivityModel,
    LegalBasisRecordModel,
    LocalizationAssessmentModel,
    TransferRecordModel,
)
from src.infrastructure.database.repositories.activity_repository import (
    SqlAlchemyActivityRepository,
)
from src.infrastructure.database.repositories.audit_repository import (
    SqlAlchemyAuditRepository,
)
from src.infrastructure.rules.engine import create_rule_engine

logger = structlog.get_logger(__name__)


class ActivityUseCases:
    def __init__(
        self,
        repo: SqlAlchemyActivityRepository,
        audit_repo: SqlAlchemyAuditRepository,
        cache: RedisCache,
    ) -> None:
        self._repo = repo
        self._audit = audit_repo
        self._cache = cache
        self._rule_engine = create_rule_engine()

    async def create_activity(
        self, tenant_id: UUID, request: CreateActivityRequest, actor_id: UUID | None = None
    ) -> ActivityResponse:
        model = DataProcessingActivityModel(
            tenant_id=str(tenant_id),
            title=request.title,
            purpose=request.purpose,
            system_name=request.system_name,
            operator_role=request.operator_role,
            retention_policy_name=request.retention_policy_name,
            cross_border_transfer=request.cross_border_transfer,
            metadata_=request.metadata,
        )
        saved = await self._repo.save(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="activity",
                resource_id=str(saved.id),
                event_type="CREATED",
                payload=request.model_dump(),
            )
        )
        await self._cache.invalidate_namespace("analytics")
        logger.info("activity_created", activity_id=str(saved.id))
        return ActivityResponse.model_validate(saved)

    async def get_activity(self, activity_id: UUID) -> ActivityResponse:
        model = await self._repo.get_by_id(activity_id)
        if not model:
            raise EntityNotFoundError("Activity", str(activity_id))
        return ActivityResponse.model_validate(model)

    async def list_activities(
        self, tenant_id: UUID, *, offset: int = 0, limit: int = 50, filters: dict[str, Any] | None = None
    ) -> list[ActivityResponse]:
        models = await self._repo.list_by_tenant(tenant_id, offset=offset, limit=limit, filters=filters)
        return [ActivityResponse.model_validate(m) for m in models]

    async def update_activity(
        self, activity_id: UUID, request: UpdateActivityRequest, actor_id: UUID | None = None
    ) -> ActivityResponse:
        model = await self._repo.get_by_id(activity_id)
        if not model:
            raise EntityNotFoundError("Activity", str(activity_id))

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "metadata":
                setattr(model, "metadata_", value)
            else:
                setattr(model, key, value)
        model.updated_at = datetime.now(UTC)

        updated = await self._repo.update(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(model.tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="activity",
                resource_id=str(activity_id),
                event_type="UPDATED",
                payload=update_data,
            )
        )
        await self._cache.invalidate_namespace("analytics")
        return ActivityResponse.model_validate(updated)

    async def add_legal_basis(
        self, activity_id: UUID, request: CreateLegalBasisRequest, actor_id: UUID | None = None
    ) -> dict[str, Any]:
        basis = LegalBasisRecordModel(
            activity_id=str(activity_id),
            basis_type=request.basis_type,
            basis_reference=request.basis_reference,
            consent_required=request.consent_required,
        )
        saved = await self._repo.save(basis)  # type: ignore[arg-type]

        await self._audit.record(
            AuditEventModel(
                tenant_id="",  # Will be filled from activity
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="legal_basis",
                resource_id=str(saved.id),
                event_type="CREATED",
                payload=request.model_dump(),
            )
        )
        return {"id": str(saved.id), "status": "created"}

    async def add_localization_assessment(
        self, activity_id: UUID, request: CreateLocalizationAssessmentRequest
    ) -> dict[str, Any]:
        assessment = LocalizationAssessmentModel(
            activity_id=str(activity_id),
            first_write_in_russia=request.first_write_in_russia,
            processor_localization_supported=request.processor_localization_supported,
            evidence_payload=request.evidence_payload,
            status="compliant" if (request.first_write_in_russia and request.processor_localization_supported) else "non_compliant",
        )
        saved = await self._repo.save(assessment)  # type: ignore[arg-type]
        return {"id": str(saved.id), "status": assessment.status}

    async def add_transfer(
        self, activity_id: UUID, request: CreateTransferRequest
    ) -> dict[str, Any]:
        transfer = TransferRecordModel(
            activity_id=str(activity_id),
            destination_country=request.destination_country,
            recipient_name=request.recipient_name,
            transfer_purpose=request.transfer_purpose,
            risk_level=request.risk_level,
            justification=request.justification,
        )
        saved = await self._repo.save(transfer)  # type: ignore[arg-type]
        return {"id": str(saved.id), "status": "created"}

    async def evaluate_risk(self, activity_id: UUID) -> list[dict[str, Any]]:
        model = await self._repo.get_by_id(activity_id)
        if not model:
            raise EntityNotFoundError("Activity", str(activity_id))

        context: dict[str, Any] = {
            "activity": {
                "id": str(model.id),
                "status": model.status,
                "localization_status": model.localization_status,
                "cross_border_transfer": model.cross_border_transfer,
            },
            "legal_bases": [
                {
                    "id": str(b.id),
                    "basis_type": b.basis_type,
                    "basis_reference": b.basis_reference,
                    "active": b.active,
                }
                for b in (model.legal_bases or [])
            ],
            "localization_assessments": [
                {
                    "id": str(a.id),
                    "first_write_in_russia": a.first_write_in_russia,
                    "processor_localization_supported": a.processor_localization_supported,
                }
                for a in (model.localization_assessments or [])
            ],
        }
        findings = self._rule_engine.evaluate(context)
        return [
            {"rule_id": f.rule_id, "severity": f.severity, "message": f.message, "details": f.details}
            for f in findings
        ]
