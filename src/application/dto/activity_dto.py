from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateActivityRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    purpose: str = Field(..., min_length=1, max_length=255)
    system_name: str = Field(..., min_length=1, max_length=255)
    operator_role: Literal["OPERATOR", "PROCESSOR", "JOINT"]
    retention_policy_name: str | None = None
    cross_border_transfer: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateActivityRequest(BaseModel):
    title: str | None = None
    purpose: str | None = None
    system_name: str | None = None
    status: str | None = None
    localization_status: str | None = None
    retention_policy_name: str | None = None
    cross_border_transfer: bool | None = None
    metadata: dict[str, Any] | None = None


class CreateLegalBasisRequest(BaseModel):
    basis_type: str
    basis_reference: str
    consent_required: bool = False


class CreateLocalizationAssessmentRequest(BaseModel):
    first_write_in_russia: bool
    processor_localization_supported: bool
    evidence_payload: dict[str, Any] = Field(default_factory=dict)


class CreateTransferRequest(BaseModel):
    destination_country: str = Field(..., min_length=2, max_length=2)
    recipient_name: str
    transfer_purpose: str
    risk_level: str
    justification: str | None = None


class ActivityResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    title: str
    purpose: str
    system_name: str
    operator_role: str
    status: str
    localization_status: str
    retention_policy_name: str | None
    cross_border_transfer: bool
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LegalBasisResponse(BaseModel):
    id: UUID
    activity_id: UUID
    basis_type: str
    basis_reference: str
    consent_required: bool
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityDetailResponse(ActivityResponse):
    legal_bases: list[LegalBasisResponse] = Field(default_factory=list)
    findings: list[dict[str, Any]] = Field(default_factory=list)
