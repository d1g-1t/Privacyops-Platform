from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateProcessorRequest(BaseModel):
    legal_name: str = Field(..., min_length=1, max_length=255)
    service_type: str
    inn: str | None = None
    hosts_personal_data: bool = False
    subprocessors_used: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateProcessorReviewRequest(BaseModel):
    questionnaire_payload: dict[str, Any]
    evidence_payload: dict[str, Any] = Field(default_factory=dict)
    risk_score: Decimal = Field(ge=0, le=100)
    localization_supported: bool = False
    dpa_present: bool = False


class ProcessorResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    legal_name: str
    inn: str | None
    service_type: str
    hosts_personal_data: bool
    subprocessors_used: bool
    status: str
    metadata: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ProcessorReviewResponse(BaseModel):
    id: UUID
    vendor_id: UUID
    review_status: str
    risk_score: Decimal
    localization_supported: bool
    dpa_present: bool
    questionnaire_payload: dict[str, Any]
    evidence_payload: dict[str, Any]
    reviewer_id: UUID | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
