from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateIncidentRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    severity: str
    detected_at: datetime
    summary: str
    system_name: str | None = None


class AddTimelineEventRequest(BaseModel):
    event_type: str
    note: str
    details: dict[str, Any] = Field(default_factory=dict)


class IncidentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    title: str
    severity: str
    status: str
    system_name: str | None
    detected_at: datetime
    reported_by: UUID | None
    summary: str
    remediation_owner_id: UUID | None
    timeline_payload: dict[str, Any]
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}
