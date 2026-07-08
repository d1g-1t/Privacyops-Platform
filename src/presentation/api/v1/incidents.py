from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from src.application.dto.incident_dto import (
    CreateIncidentRequest,
    IncidentResponse,
    UpdateIncidentRequest,
)
from src.application.use_cases.incident_use_cases import IncidentUseCases
from fastapi import Depends

from src.infrastructure.security.rbac import require_dpo
from src.presentation.deps import (
    CurrentTenantId,
    CurrentUserId,
    get_incident_use_cases,
)

router = APIRouter(prefix="/incidents", tags=["incidents"], dependencies=[Depends(require_dpo)])


@router.post("", response_model=IncidentResponse, status_code=201, response_class=ORJSONResponse)
async def create_incident(
    body: CreateIncidentRequest,
    tenant_id: CurrentTenantId,
    user_id: CurrentUserId,
    uc: IncidentUseCases = Depends(get_incident_use_cases),
):
    return await uc.create_incident(tenant_id, body, actor_id=user_id)


@router.get("", response_model=list[IncidentResponse], response_class=ORJSONResponse)
async def list_incidents(
    tenant_id: CurrentTenantId,
    uc: IncidentUseCases = Depends(get_incident_use_cases),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await uc.list_incidents(tenant_id, offset=offset, limit=limit)


@router.get("/rkn-report", response_class=ORJSONResponse)
async def rkn_report(
    tenant_id: CurrentTenantId,
    uc: IncidentUseCases = Depends(get_incident_use_cases),
):
    return await uc.get_rkn_report(tenant_id)


@router.get("/{incident_id}", response_model=IncidentResponse, response_class=ORJSONResponse)
async def get_incident(
    incident_id: UUID,
    uc: IncidentUseCases = Depends(get_incident_use_cases),
):
    return await uc.get_incident(incident_id)


@router.patch("/{incident_id}", response_model=IncidentResponse, response_class=ORJSONResponse)
async def update_incident(
    incident_id: UUID,
    body: UpdateIncidentRequest,
    user_id: CurrentUserId,
    uc: IncidentUseCases = Depends(get_incident_use_cases),
):
    return await uc.update_incident(incident_id, body, actor_id=user_id)
