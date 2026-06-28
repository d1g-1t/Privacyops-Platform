from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import structlog

from src.application.dto.analytics_dto import (
    AnalyticsDashboardResponse,
    ComplianceScoreResponse,
    TrendPointResponse,
)
from src.infrastructure.database.repositories.activity_repository import (
    SqlAlchemyActivityRepository,
)
from src.infrastructure.database.repositories.consent_repository import (
    SqlAlchemyConsentRepository,
)
from src.infrastructure.database.repositories.dsr_repository import SqlAlchemyDSRRepository
from src.infrastructure.database.repositories.incident_repository import (
    SqlAlchemyIncidentRepository,
)
from src.infrastructure.database.repositories.processor_repository import (
    SqlAlchemyProcessorRepository,
)
from src.infrastructure.cache.redis_cache import RedisCache

logger = structlog.get_logger(__name__)


class AnalyticsUseCases:
    def __init__(
        self,
        activity_repo: SqlAlchemyActivityRepository,
        consent_repo: SqlAlchemyConsentRepository,
        dsr_repo: SqlAlchemyDSRRepository,
        incident_repo: SqlAlchemyIncidentRepository,
        processor_repo: SqlAlchemyProcessorRepository,
        cache: RedisCache,
    ) -> None:
        self._activity = activity_repo
        self._consent = consent_repo
        self._dsr = dsr_repo
        self._incident = incident_repo
        self._processor = processor_repo
        self._cache = cache

    async def get_dashboard(self, tenant_id: UUID) -> AnalyticsDashboardResponse:
        cache_key = f"analytics:dashboard:{tenant_id}"
        cached = await self._cache.get(cache_key)
        if cached:
            return AnalyticsDashboardResponse(**cached)

        activities = await self._activity.list_by_tenant(tenant_id, offset=0, limit=10000)
        total_activities = len(activities)
        active_activities = sum(1 for a in activities if a.status == "ACTIVE")
        draft_activities = sum(1 for a in activities if a.status == "DRAFT")

        incidents = await self._incident.list_by_tenant(tenant_id, offset=0, limit=10000)
        open_incidents = sum(1 for i in incidents if i.status not in ("CLOSED", "REMEDIATED"))
        critical_incidents = sum(1 for i in incidents if i.severity == "CRITICAL")

        dsr_stats = await self._dsr.dashboard_stats(tenant_id)

        processors = await self._processor.list_by_tenant(tenant_id, offset=0, limit=10000)
        active_processors = sum(1 for p in processors if getattr(p, "status", None) == "ACTIVE")
        pending_processors = sum(1 for p in processors if getattr(p, "status", None) == "PENDING")

        score = self._calculate_compliance_score(
            total_activities=total_activities,
            active_activities=active_activities,
            open_incidents=open_incidents,
            critical_incidents=critical_incidents,
            dsr_stats=dsr_stats,
        )

        result = AnalyticsDashboardResponse(
            total_activities=total_activities,
            active_activities=active_activities,
            draft_activities=draft_activities,
            open_incidents=open_incidents,
            critical_incidents=critical_incidents,
            dsr_total=dsr_stats.get("total", 0),
            dsr_open=dsr_stats.get("open", 0),
            dsr_overdue=dsr_stats.get("overdue", 0),
            active_processors=active_processors,
            pending_processors=pending_processors,
            compliance_score=score,
            generated_at=datetime.now(UTC),
        )
        await self._cache.set(cache_key, result.model_dump(mode="json"), ttl=900)
        return result

    async def get_compliance_score(self, tenant_id: UUID) -> ComplianceScoreResponse:
        dashboard = await self.get_dashboard(tenant_id)
        return ComplianceScoreResponse(
            overall_score=dashboard.compliance_score,
            breakdown={
                "activities_registered": min(dashboard.active_activities * 5, 25),
                "incident_management": max(0, 25 - dashboard.open_incidents * 5),
                "dsr_compliance": max(0, 25 - dashboard.dsr_overdue * 8),
                "processor_oversight": min(dashboard.active_processors * 5, 25),
            },
            generated_at=datetime.now(UTC),
        )

    async def get_trend(
        self, tenant_id: UUID, *, days: int = 30
    ) -> list[TrendPointResponse]:
        now = datetime.now(UTC)
        points = []
        for i in range(days):
            day = now - timedelta(days=days - i - 1)
            points.append(
                TrendPointResponse(
                    date=day.date(),
                    label=day.strftime("%Y-%m-%d"),
                    value=0,
                )
            )
        return points

    def _calculate_compliance_score(
        self,
        *,
        total_activities: int,
        active_activities: int,
        open_incidents: int,
        critical_incidents: int,
        dsr_stats: dict[str, Any],
    ) -> float:
        score = 100.0

        if total_activities == 0:
            score -= 30.0
        elif active_activities / max(total_activities, 1) < 0.5:
            score -= 15.0

        score -= critical_incidents * 10.0
        score -= open_incidents * 3.0

        overdue = dsr_stats.get("overdue", 0)
        score -= overdue * 8.0

        return max(0.0, min(100.0, round(score, 1)))
