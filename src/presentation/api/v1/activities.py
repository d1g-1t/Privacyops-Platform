from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from src.application.dto.activity_dto import (
    ActivityDetailResponse,
    ActivityResponse,
    CreateActivityRequest,
    UpdateActivityRequest,
)
from src.application.use_cases.activity_use_cases import ActivityUseCases
from src.infrastructure.security.rbac import require_compliance
from src.presentation.deps import (
    CurrentTenantId,
    CurrentUserId,
    get_activity_use_cases,
)

router = APIRouter(prefix="/activities", tags=["activities"], dependencies=[require_compliance])


@router.post("", response_model=ActivityResponse, status_code=201, response_class=ORJSONResponse)
async def create_activity(
    body: CreateActivityRequest,
    tenant_id: CurrentTenantId,
    user_id: CurrentUserId,
    uc: ActivityUseCases = Depends(get_activity_use_cases),
):
    return await uc.create(tenant_id, body, actor_id=user_id)


@router.get("", response_model=list[ActivityResponse], response_class=ORJSONResponse)
async def list_activities(
    tenant_id: CurrentTenantId,
    uc: ActivityUseCases = Depends(get_activity_use_cases),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await uc.list(tenant_id, offset=offset, limit=limit)


@router.get("/{activity_id}", response_model=ActivityDetailResponse, response_class=ORJSONResponse)
async def get_activity(
    activity_id: UUID,
    uc: ActivityUseCases = Depends(get_activity_use_cases),
):
    return await uc.get(activity_id)


@router.patch("/{activity_id}", response_model=ActivityResponse, response_class=ORJSONResponse)
async def update_activity(
    activity_id: UUID,
    body: UpdateActivityRequest,
    user_id: CurrentUserId,
    uc: ActivityUseCases = Depends(get_activity_use_cases),
):
    return await uc.update(activity_id, body, actor_id=user_id)


@router.post(
    "/{activity_id}/evaluate-risk",
    response_class=ORJSONResponse,
)
async def evaluate_risk(
    activity_id: UUID,
    user_id: CurrentUserId,
    uc: ActivityUseCases = Depends(get_activity_use_cases),
):
    return await uc.evaluate_risk(activity_id, actor_id=user_id)
