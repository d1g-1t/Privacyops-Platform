from __future__ import annotations

from src.domain.entities.consent_capture import ConsentCapture
from src.domain.entities.legal_basis_record import LegalBasisRecord
from src.domain.value_objects.consent_status import ConsentStatus
from src.domain.value_objects.legal_basis_type import LegalBasisType


class ConsentDomainService:
    @staticmethod
    def activity_has_valid_consent(
        bases: list[LegalBasisRecord],
        captures: list[ConsentCapture],
    ) -> bool:
        consent_bases = [
            b for b in bases if b.basis_type == LegalBasisType.CONSENT and b.active
        ]
        if not consent_bases:
            return True

        active_captures = [c for c in captures if c.status == ConsentStatus.ACTIVE]
        return len(active_captures) > 0

    @staticmethod
    def find_orphaned_captures(
        bases: list[LegalBasisRecord],
        captures: list[ConsentCapture],
    ) -> list[ConsentCapture]:
        basis_activity_ids = {b.activity_id for b in bases if b.active}
        return [
            c
            for c in captures
            if c.activity_id and c.activity_id not in basis_activity_ids
        ]
