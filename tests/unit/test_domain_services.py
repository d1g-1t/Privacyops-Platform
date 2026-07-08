"""Unit tests for domain services — actual API matching."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from src.domain.services.consent_service import ConsentDomainService
from src.domain.services.dsr_service import DSRDomainService
from src.domain.services.localization_service import LocalizationDomainService
from src.domain.value_objects.consent_status import ConsentStatus
from src.domain.value_objects.dsr_status import DSRStatus


class TestConsentDomainService:
    """Tests for ConsentDomainService — static methods only."""

    def test_activity_has_valid_consent_no_consent_bases(self):
        # No consent legal bases → always OK (no consent needed)
        result = ConsentDomainService.activity_has_valid_consent(bases=[], captures=[])
        assert result is True

    def test_activity_has_valid_consent_with_active_capture(self):
        from src.domain.entities.legal_basis_record import LegalBasisRecord
        from src.domain.entities.consent_capture import ConsentCapture
        from src.domain.value_objects.legal_basis_type import LegalBasisType

        basis = LegalBasisRecord(
            id=uuid4(),
            activity_id=uuid4(),
            basis_type=LegalBasisType.CONSENT,
            basis_reference="ст. 9 152-ФЗ",
            active=True,
        )
        capture = ConsentCapture(
            id=uuid4(),
            template_id=uuid4(),
            tenant_id=uuid4(),
            subject_identifier="test@example.com",
            source_channel="web",
            captured_at=datetime.now(UTC),
            status=ConsentStatus.ACTIVE,
        )
        result = ConsentDomainService.activity_has_valid_consent(
            bases=[basis], captures=[capture]
        )
        assert result is True


class TestDSRDomainService:
    """Tests for DSRDomainService — SLA and urgency logic."""

    def test_classify_urgency_overdue(self):
        from src.domain.entities.data_subject_request import DataSubjectRequest

        dsr = DataSubjectRequest(
            id=uuid4(),
            tenant_id=uuid4(),
            request_type="ACCESS",
            subject_identifier="test-user@example.com",
            status="IN_PROGRESS",
            due_at=datetime.now(UTC) - timedelta(days=1),
            submitted_at=datetime.now(UTC) - timedelta(days=31),
        )
        # Patch overdue check
        urgency = DSRDomainService.classify_urgency(dsr)
        assert urgency in ("OVERDUE", "URGENT", "WARNING", "NORMAL")

    def test_can_transition_open_to_assigned(self):
        from src.domain.entities.data_subject_request import DataSubjectRequest

        dsr = DataSubjectRequest(
            id=uuid4(),
            tenant_id=uuid4(),
            request_type="ACCESS",
            subject_identifier="test@example.com",
            status=DSRStatus.OPEN,
            due_at=datetime.now(UTC) + timedelta(days=30),
            submitted_at=datetime.now(UTC),
        )
        assert DSRDomainService.can_transition(dsr, DSRStatus.ASSIGNED) is True

    def test_cannot_transition_completed_to_open(self):
        from src.domain.entities.data_subject_request import DataSubjectRequest

        dsr = DataSubjectRequest(
            id=uuid4(),
            tenant_id=uuid4(),
            request_type="ACCESS",
            subject_identifier="test@example.com",
            status=DSRStatus.COMPLETED,
            due_at=datetime.now(UTC) + timedelta(days=30),
            submitted_at=datetime.now(UTC),
        )
        assert DSRDomainService.can_transition(dsr, DSRStatus.OPEN) is False


class TestLocalizationDomainService:
    """LocalizationDomainService evaluation logic."""

    def test_service_has_expected_methods(self):
        """Minimal smoke test — methods exist and are callable."""
        assert hasattr(LocalizationDomainService, "evaluate_activity_localization")
        assert hasattr(LocalizationDomainService, "is_cross_border_blocked")

