from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from src.application.dto.dsr_dto import (
    AssignDSRRequest,
    CreateDSRRequest,
    DSRDashboardResponse,
    DSRResponse,
    RespondDSRRequest,
)
from src.application.use_cases.dsr_use_cases import DSRUseCases
from src.infrastructure.security.rbac import require_dpo
from src.presentation.deps import (
    CurrentTenantId,
    CurrentUserId,
    get_dsr_use_cases,
)

router = APIRouter(prefix="/dsr", tags=["dsr"], dependencies=[require_dpo])


@router.post("", response_model=DSRResponse, status_code=201, response_class=ORJSONResponse)
async def create_dsr(
    body: CreateDSRRequest,
    tenant_id: CurrentTenantId,
    user_id: CurrentUserId,
    uc: DSRUseCases = Depends(get_dsr_use_cases),
):
    return await uc.create(tenant_id, body, actor_id=user_id)


@router.get("", response_model=list[DSRResponse], response_class=ORJSONResponse)
async def list_dsrs(
    tenant_id: CurrentTenantId,
    uc: DSRUseCases = Depends(get_dsr_use_cases),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await uc.list(tenant_id, offset=offset, limit=limit)


@router.get("/dashboard", response_model=DSRDashboardResponse, response_class=ORJSONResponse)
async def dsr_dashboard(
    tenant_id: CurrentTenantId,
    uc: DSRUseCases = Depends(get_dsr_use_cases),
):
    return await uc.dashboard(tenant_id)


@router.get("/{dsr_id}", response_model=DSRResponse, response_class=ORJSONResponse)
async def get_dsr(
    dsr_id: UUID,
    uc: DSRUseCases = Depends(get_dsr_use_cases),
):
    return await uc.get(dsr_id)


@router.post("/{dsr_id}/assign", response_model=DSRResponse, response_class=ORJSONResponse)
async def assign_dsr(
    dsr_id: UUID,
    body: AssignDSRRequest,
    user_id: CurrentUserId,
    uc: DSRUseCases = Depends(get_dsr_use_cases),
):
    return await uc.assign(dsr_id, body.assignee_id, actor_id=user_id)


@router.post("/{dsr_id}/respond", response_model=DSRResponse, response_class=ORJSONResponse)
async def respond_dsr(
    dsr_id: UUID,
    body: RespondDSRRequest,
    user_id: CurrentUserId,
    uc: DSRUseCases = Depends(get_dsr_use_cases),
):
    return await uc.respond(dsr_id, body.response_text, actor_id=user_id)


@router.post("/{dsr_id}/complete", response_model=DSRResponse, response_class=ORJSONResponse)
async def complete_dsr(
    dsr_id: UUID,
    user_id: CurrentUserId,
    uc: DSRUseCases = Depends(get_dsr_use_cases),
):
    return await uc.complete(dsr_id, actor_id=user_id)
