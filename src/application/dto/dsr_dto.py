from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateDSRRequest(BaseModel):
    request_type: Literal["ACCESS", "CORRECTION", "DELETION", "OBJECTION", "RESTRICTION"]
    subject_identifier: str
    due_at: datetime


class AssignDSRRequest(BaseModel):
    assigned_user_id: UUID


class RespondDSRRequest(BaseModel):
    response_payload: dict[str, Any]


class CompleteDSRRequest(BaseModel):
    evidence_payload: dict[str, Any] = Field(default_factory=dict)


class DSRResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    request_type: str
    subject_identifier: str
    status: str
    submitted_at: datetime
    due_at: datetime
    assigned_user_id: UUID | None
    response_payload: dict[str, Any]
    evidence_payload: dict[str, Any]
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class DSRDashboardResponse(BaseModel):
    total: int
    open: int
    overdue: int
    completed: int
