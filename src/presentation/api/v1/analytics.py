from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from src.application.dto.analytics_dto import (
    AnalyticsDashboardResponse,
    ComplianceScoreResponse,
    TrendPointResponse,
)
from src.application.use_cases.analytics_use_cases import AnalyticsUseCases
from fastapi import Depends

from src.infrastructure.security.rbac import require_viewer
from src.presentation.deps import (
    CurrentTenantId,
    get_analytics_use_cases,
)

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(require_viewer)])


@router.get("/dashboard", response_model=AnalyticsDashboardResponse, response_class=ORJSONResponse)
async def dashboard(
    tenant_id: CurrentTenantId,
    uc: AnalyticsUseCases = Depends(get_analytics_use_cases),
):
    return await uc.get_dashboard(tenant_id)


@router.get(
    "/compliance-score",
    response_model=ComplianceScoreResponse,
    response_class=ORJSONResponse,
)
async def compliance_score(
    tenant_id: CurrentTenantId,
    uc: AnalyticsUseCases = Depends(get_analytics_use_cases),
):
    return await uc.get_compliance_score(tenant_id)


@router.get(
    "/trend",
    response_model=list[TrendPointResponse],
    response_class=ORJSONResponse,
)
async def trend(
    tenant_id: CurrentTenantId,
    uc: AnalyticsUseCases = Depends(get_analytics_use_cases),
    days: int = Query(30, ge=1, le=365),
):
    return await uc.get_trend(tenant_id, days=days)
