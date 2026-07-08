from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

from src.application.dto.processor_dto import (
    CreateProcessorRequest,
    CreateProcessorReviewRequest,
    ProcessorResponse,
    ProcessorReviewResponse,
)
from src.application.use_cases.processor_use_cases import ProcessorUseCases
from fastapi import Depends

from src.infrastructure.security.rbac import require_compliance
from src.presentation.deps import (
    CurrentTenantId,
    CurrentUserId,
    get_processor_use_cases,
)

router = APIRouter(prefix="/processors", tags=["processors"], dependencies=[Depends(require_compliance)])


class RejectBody(BaseModel):
    reason: str


@router.post("", response_model=ProcessorResponse, status_code=201, response_class=ORJSONResponse)
async def create_processor(
    body: CreateProcessorRequest,
    tenant_id: CurrentTenantId,
    user_id: CurrentUserId,
    uc: ProcessorUseCases = Depends(get_processor_use_cases),
):
    return await uc.create_processor(tenant_id, body, actor_id=user_id)


@router.get("", response_model=list[ProcessorResponse], response_class=ORJSONResponse)
async def list_processors(
    tenant_id: CurrentTenantId,
    uc: ProcessorUseCases = Depends(get_processor_use_cases),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await uc.list_processors(tenant_id, offset=offset, limit=limit)


@router.get("/{vendor_id}", response_model=ProcessorResponse, response_class=ORJSONResponse)
async def get_processor(
    vendor_id: UUID,
    uc: ProcessorUseCases = Depends(get_processor_use_cases),
):
    return await uc.get_processor(vendor_id)


@router.post(
    "/{vendor_id}/reviews",
    response_model=ProcessorReviewResponse,
    status_code=201,
    response_class=ORJSONResponse,
)
async def create_review(
    vendor_id: UUID,
    body: CreateProcessorReviewRequest,
    user_id: CurrentUserId,
    uc: ProcessorUseCases = Depends(get_processor_use_cases),
):
    return await uc.create_review(vendor_id, body, actor_id=user_id)


@router.get(
    "/{vendor_id}/reviews",
    response_model=list[ProcessorReviewResponse],
    response_class=ORJSONResponse,
)
async def get_reviews(
    vendor_id: UUID,
    uc: ProcessorUseCases = Depends(get_processor_use_cases),
):
    return await uc.get_reviews(vendor_id)


@router.post("/{vendor_id}/approve", response_model=ProcessorResponse, response_class=ORJSONResponse)
async def approve_processor(
    vendor_id: UUID,
    user_id: CurrentUserId,
    uc: ProcessorUseCases = Depends(get_processor_use_cases),
):
    return await uc.approve_processor(vendor_id, actor_id=user_id)


@router.post("/{vendor_id}/reject", response_model=ProcessorResponse, response_class=ORJSONResponse)
async def reject_processor(
    vendor_id: UUID,
    body: RejectBody,
    user_id: CurrentUserId,
    uc: ProcessorUseCases = Depends(get_processor_use_cases),
):
    return await uc.reject_processor(vendor_id, body.reason, actor_id=user_id)
