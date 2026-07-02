from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from src.application.dto.consent_dto import (
    CaptureConsentRequest,
    ConsentCaptureResponse,
    ConsentTemplateResponse,
    CreateConsentTemplateRequest,
)
from src.application.use_cases.consent_use_cases import ConsentUseCases
from src.infrastructure.security.rbac import require_compliance
from src.presentation.deps import (
    CurrentTenantId,
    CurrentUserId,
    get_consent_use_cases,
)

router = APIRouter(prefix="/consents", tags=["consents"], dependencies=[require_compliance])


@router.post(
    "/templates",
    response_model=ConsentTemplateResponse,
    status_code=201,
    response_class=ORJSONResponse,
)
async def create_template(
    body: CreateConsentTemplateRequest,
    tenant_id: CurrentTenantId,
    user_id: CurrentUserId,
    uc: ConsentUseCases = Depends(get_consent_use_cases),
):
    return await uc.create_template(tenant_id, body, actor_id=user_id)


@router.get(
    "/templates",
    response_model=list[ConsentTemplateResponse],
    response_class=ORJSONResponse,
)
async def list_templates(
    tenant_id: CurrentTenantId,
    uc: ConsentUseCases = Depends(get_consent_use_cases),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await uc.list_templates(tenant_id, offset=offset, limit=limit)


@router.post(
    "/captures",
    response_model=ConsentCaptureResponse,
    status_code=201,
    response_class=ORJSONResponse,
)
async def capture_consent(
    body: CaptureConsentRequest,
    tenant_id: CurrentTenantId,
    user_id: CurrentUserId,
    uc: ConsentUseCases = Depends(get_consent_use_cases),
):
    return await uc.capture_consent(tenant_id, body, actor_id=user_id)


@router.get(
    "/captures",
    response_model=list[ConsentCaptureResponse],
    response_class=ORJSONResponse,
)
async def list_captures(
    tenant_id: CurrentTenantId,
    uc: ConsentUseCases = Depends(get_consent_use_cases),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await uc.list_captures(tenant_id, offset=offset, limit=limit)


@router.post(
    "/captures/{capture_id}/withdraw",
    response_model=ConsentCaptureResponse,
    response_class=ORJSONResponse,
)
async def withdraw_consent(
    capture_id: UUID,
    user_id: CurrentUserId,
    uc: ConsentUseCases = Depends(get_consent_use_cases),
):
    return await uc.withdraw_consent(capture_id, actor_id=user_id)
