from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateConsentTemplateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: int = Field(default=1, ge=1)
    channel: str = Field(..., min_length=1, max_length=64)
    text_body: str = Field(..., min_length=1)
    language_code: str = "ru"


class CreateConsentCaptureRequest(BaseModel):
    subject_identifier: str
    template_id: UUID
    activity_id: UUID | None = None
    source_channel: str
    proof_payload: dict[str, Any] = Field(default_factory=dict)


class ConsentTemplateResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    version: int
    language_code: str
    channel: str
    text_body: str
    active: bool
    checksum: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConsentCaptureResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    subject_identifier: str
    template_id: UUID
    activity_id: UUID | None
    status: str
    captured_at: datetime
    withdrawn_at: datetime | None
    source_channel: str
    proof_payload: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
