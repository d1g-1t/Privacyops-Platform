from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.value_objects.incident_severity import IncidentSeverity


@dataclass
class PrivacyIncident:
    tenant_id: UUID
    title: str
    severity: IncidentSeverity
    detected_at: datetime
    summary: str

    id: UUID = field(default_factory=uuid4)
    status: str = "OPEN"
    system_name: str | None = None
    reported_by: UUID | None = None
    remediation_owner_id: UUID | None = None
    timeline_payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None

    def add_timeline_event(self, event: dict[str, Any]) -> None:
        events: list[dict[str, Any]] = self.timeline_payload.setdefault("events", [])
        event["timestamp"] = datetime.now(UTC).isoformat()
        events.append(event)

    def resolve(self) -> None:
        self.status = "RESOLVED"
        self.resolved_at = datetime.now(UTC)
        self.add_timeline_event({"type": "resolved", "note": "Incident resolved"})

    @property
    def is_critical(self) -> bool:
        return self.severity in (IncidentSeverity.CRITICAL, IncidentSeverity.HIGH)
