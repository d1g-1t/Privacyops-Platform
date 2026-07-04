from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4


@dataclass
class ProcessorReview:
    vendor_id: UUID
    risk_score: Decimal

    id: UUID = field(default_factory=uuid4)
    review_status: str = "PENDING"
    localization_supported: bool = False
    dpa_present: bool = False
    questionnaire_payload: dict[str, Any] = field(default_factory=dict)
    evidence_payload: dict[str, Any] = field(default_factory=dict)
    reviewer_id: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def complete(self) -> None:
        self.review_status = "COMPLETED"
        self.completed_at = datetime.now(UTC)

    @property
    def is_high_risk(self) -> bool:
        return self.risk_score >= Decimal("70")

    @property
    def should_reject(self) -> bool:
        return self.risk_score >= Decimal("80")
