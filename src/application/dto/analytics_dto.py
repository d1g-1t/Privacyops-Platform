from __future__ import annotations

from datetime import date, datetime
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


class AnalyticsDashboardResponse(BaseModel):
    total_activities: int = 0
    active_activities: int = 0
    draft_activities: int = 0
    open_incidents: int = 0
    critical_incidents: int = 0
    dsr_total: int = 0
    dsr_open: int = 0
    dsr_overdue: int = 0
    active_processors: int = 0
    pending_processors: int = 0
    compliance_score: float = 100.0
    generated_at: datetime | None = None


class ComplianceScoreResponse(BaseModel):
    overall_score: float = 100.0
    breakdown: dict[str, float] = {}
    generated_at: datetime | None = None


class TrendPointResponse(BaseModel):
    date: date
    label: str
    value: float = 0.0
