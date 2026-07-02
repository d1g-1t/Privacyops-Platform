from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.value_objects.localization_status import LocalizationStatus


@dataclass
class LocalizationAssessment:
    activity_id: UUID
    first_write_in_russia: bool
    processor_localization_supported: bool

    id: UUID = field(default_factory=uuid4)
    evidence_payload: dict[str, Any] = field(default_factory=dict)
    status: LocalizationStatus = LocalizationStatus.UNDER_REVIEW
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def evaluate(self, *, strict_mode: bool = True) -> LocalizationStatus:
        if self.first_write_in_russia and self.processor_localization_supported:
            self.status = LocalizationStatus.COMPLIANT
        elif strict_mode:
            self.status = LocalizationStatus.NON_COMPLIANT
        else:
            self.status = LocalizationStatus.UNDER_REVIEW
        return self.status
