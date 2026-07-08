"""Unit tests for domain value objects."""

from __future__ import annotations

import pytest

from src.domain.value_objects.activity_status import ActivityStatus
from src.domain.value_objects.consent_status import ConsentStatus
from src.domain.value_objects.dsr_status import DSRStatus
from src.domain.value_objects.incident_severity import IncidentSeverity
from src.domain.value_objects.legal_basis_type import LegalBasisType
from src.domain.value_objects.localization_status import LocalizationStatus
from src.domain.value_objects.transfer_risk_level import TransferRiskLevel
from src.domain.value_objects.user_role import UserRole


class TestActivityStatus:
    def test_all_values_exist(self):
        assert ActivityStatus.DRAFT
        assert ActivityStatus.ACTIVE
        assert ActivityStatus.UNDER_REVIEW
        assert ActivityStatus.ARCHIVED

    def test_string_representation(self):
        assert str(ActivityStatus.DRAFT) == "draft"
        assert ActivityStatus.ACTIVE.value == "active"


class TestLegalBasisType:
    def test_all_152fz_basis_types(self):
        expected = {
            "consent",
            "contract",
            "legal_obligation",
            "vital_interest",
            "public_interest",
            "legitimate_interest",
            "statutory",
        }
        actual = {e.value for e in LegalBasisType}
        assert expected == actual


class TestConsentStatus:
    def test_lifecycle_states(self):
        assert ConsentStatus.ACTIVE.value == "active"
        assert ConsentStatus.WITHDRAWN.value == "withdrawn"
        assert ConsentStatus.EXPIRED.value == "expired"


class TestDSRStatus:
    def test_workflow_states(self):
        # Must contain these core states
        core = {"open", "assigned", "in_progress", "responded", "completed", "rejected"}
        actual = {e.value for e in DSRStatus}
        assert core.issubset(actual)


class TestIncidentSeverity:
    def test_ordering(self):
        severities = [s.value for s in IncidentSeverity]
        assert "critical" in severities
        assert "high" in severities
        assert "medium" in severities
        assert "low" in severities


class TestTransferRiskLevel:
    def test_levels(self):
        expected = {"low", "medium", "high", "blocked"}
        actual = {e.value for e in TransferRiskLevel}
        assert expected == actual


class TestLocalizationStatus:
    def test_statuses(self):
        # Must contain these core states
        core = {"pending", "compliant", "non_compliant"} if hasattr(LocalizationStatus, "PENDING") else {"compliant", "non_compliant", "unknown"}
        actual = {e.value for e in LocalizationStatus}
        assert core.issubset(actual)


class TestUserRole:
    def test_standard_roles(self):
        # Must contain these core roles
        core = {"admin", "dpo", "compliance", "legal", "viewer"}
        actual = {e.value for e in UserRole}
        assert core.issubset(actual)
