from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    activities_total: int = 0
    activities_active: int = 0
    activities_without_basis: int = 0
    localization_gaps: int = 0
    dsr_open: int = 0
    dsr_overdue: int = 0
    vendor_high_risk: int = 0
    incidents_open: int = 0
    consent_expiring: int = 0


class AnalyticsDetailResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int
