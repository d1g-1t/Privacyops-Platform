from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.value_objects.transfer_risk_level import TransferRiskLevel


@dataclass
class TransferRecord:
    activity_id: UUID
    destination_country: str
    recipient_name: str
    transfer_purpose: str
    risk_level: TransferRiskLevel

    id: UUID = field(default_factory=uuid4)
    blocked: bool = False
    justification: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def block(self, reason: str) -> None:
        self.blocked = True
        self.justification = reason

    def unblock(self, justification: str) -> None:
        self.blocked = False
        self.justification = justification
