from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.value_objects.consent_status import ConsentStatus


@dataclass
class ConsentCapture:
    tenant_id: UUID
    subject_identifier: str
    template_id: UUID
    source_channel: str
    captured_at: datetime

    id: UUID = field(default_factory=uuid4)
    activity_id: UUID | None = None
    status: ConsentStatus = ConsentStatus.ACTIVE
    withdrawn_at: datetime | None = None
    proof_payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def withdraw(self) -> None:
        if self.status == ConsentStatus.WITHDRAWN:
            raise ValueError("Consent already withdrawn")
        self.status = ConsentStatus.WITHDRAWN
        self.withdrawn_at = datetime.now(UTC)

    @property
    def is_valid(self) -> bool:
        return self.status == ConsentStatus.ACTIVE
