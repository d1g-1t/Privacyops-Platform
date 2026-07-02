from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import structlog

from src.application.dto.consent_dto import (
    ConsentCaptureResponse,
    ConsentTemplateResponse,
    CreateConsentCaptureRequest,
    CreateConsentTemplateRequest,
)
from src.domain.exceptions import EntityNotFoundError
from src.infrastructure.database.models import (
    AuditEventModel,
    ConsentCaptureModel,
    ConsentTemplateModel,
)
from src.infrastructure.database.repositories.audit_repository import SqlAlchemyAuditRepository
from src.infrastructure.database.repositories.consent_repository import SqlAlchemyConsentRepository

logger = structlog.get_logger(__name__)


class ConsentUseCases:
    def __init__(
        self,
        repo: SqlAlchemyConsentRepository,
        audit_repo: SqlAlchemyAuditRepository,
    ) -> None:
        self._repo = repo
        self._audit = audit_repo

    async def create_template(
        self, tenant_id: UUID, request: CreateConsentTemplateRequest
    ) -> ConsentTemplateResponse:
        checksum = hashlib.sha256(
            f"{request.name}:{request.version}:{request.text_body}".encode()
        ).hexdigest()
        model = ConsentTemplateModel(
            tenant_id=str(tenant_id),
            name=request.name,
            version=request.version,
            language_code=request.language_code,
            channel=request.channel,
            text_body=request.text_body,
            checksum=checksum,
        )
        saved = await self._repo.save_template(model)
        logger.info("consent_template_created", template_id=str(saved.id))
        return ConsentTemplateResponse.model_validate(saved)

    async def list_templates(
        self, tenant_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> list[ConsentTemplateResponse]:
        models = await self._repo.list_templates(tenant_id, offset=offset, limit=limit)
        return [ConsentTemplateResponse.model_validate(m) for m in models]

    async def capture_consent(
        self, tenant_id: UUID, request: CreateConsentCaptureRequest, actor_id: UUID | None = None
    ) -> ConsentCaptureResponse:
        template = await self._repo.get_template(request.template_id)
        if not template:
            raise EntityNotFoundError("ConsentTemplate", str(request.template_id))

        model = ConsentCaptureModel(
            tenant_id=str(tenant_id),
            subject_identifier=request.subject_identifier,
            template_id=str(request.template_id),
            activity_id=str(request.activity_id) if request.activity_id else None,
            status="active",
            captured_at=datetime.now(UTC),
            source_channel=request.source_channel,
            proof_payload=request.proof_payload,
        )
        saved = await self._repo.save(model)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="consent_capture",
                resource_id=str(saved.id),
                event_type="CREATED",
                payload={"subject": request.subject_identifier, "template_id": str(request.template_id)},
            )
        )
        logger.info("consent_captured", capture_id=str(saved.id))
        return ConsentCaptureResponse.model_validate(saved)

    async def list_captures(
        self, tenant_id: UUID, *, offset: int = 0, limit: int = 50
    ) -> list[ConsentCaptureResponse]:
        models = await self._repo.list_by_tenant(tenant_id, offset=offset, limit=limit)
        return [ConsentCaptureResponse.model_validate(m) for m in models]

    async def withdraw_consent(
        self, capture_id: UUID, actor_id: UUID | None = None
    ) -> ConsentCaptureResponse:
        model = await self._repo.withdraw(capture_id)

        await self._audit.record(
            AuditEventModel(
                tenant_id=str(model.tenant_id),
                actor_user_id=str(actor_id) if actor_id else None,
                resource_type="consent_capture",
                resource_id=str(capture_id),
                event_type="WITHDRAWN",
                payload={"withdrawn_at": model.withdrawn_at.isoformat() if model.withdrawn_at else None},
            )
        )
        logger.info("consent_withdrawn", capture_id=str(capture_id))
        return ConsentCaptureResponse.model_validate(model)

    async def find_expiring(self, tenant_id: UUID, *, before: datetime) -> list[ConsentCaptureResponse]:
        models = await self._repo.find_expiring(tenant_id, before=before)
        return [ConsentCaptureResponse.model_validate(m) for m in models]
