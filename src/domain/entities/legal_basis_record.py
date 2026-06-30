from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.value_objects.legal_basis_type import LegalBasisType


@dataclass
class LegalBasisRecord:
    activity_id: UUID
    basis_type: LegalBasisType
    basis_reference: str

    id: UUID = field(default_factory=uuid4)
    consent_required: bool = False
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def deactivate(self) -> None:
        self.active = False

    @property
    def requires_consent_capture(self) -> bool:
        return self.basis_type == LegalBasisType.CONSENT or self.consent_required
