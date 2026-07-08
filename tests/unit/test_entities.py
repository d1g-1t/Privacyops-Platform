"""Unit tests for domain entities — business logic & computed properties."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from src.domain.entities.data_processing_activity import DataProcessingActivity
from src.domain.entities.data_subject_request import DataSubjectRequest
from src.domain.value_objects.activity_status import ActivityStatus
from src.domain.value_objects.dsr_status import DSRStatus
from src.domain.value_objects.localization_status import LocalizationStatus


class TestDataProcessingActivity:
    def _make_activity(self, **kwargs) -> DataProcessingActivity:
        defaults = dict(
            tenant_id=uuid4(),
            title="Обработка кадровых данных",
            purpose="Учёт персонала",
            system_name="HR System",
            operator_role="OPERATOR",
        )
        defaults.update(kwargs)
        return DataProcessingActivity(**defaults)

    def test_default_status_is_draft(self):
        a = self._make_activity()
        assert a.status == ActivityStatus.DRAFT

    def test_activate_from_draft(self):
        a = self._make_activity()
        a.activate()
        assert a.status == ActivityStatus.ACTIVE

    def test_activate_from_active_raises(self):
        a = self._make_activity()
        a.status = ActivityStatus.ACTIVE
        with pytest.raises(ValueError):
            a.activate()

    def test_suspend_sets_status(self):
        a = self._make_activity()
        a.status = ActivityStatus.ACTIVE
        a.suspend("Security review")
        assert a.status == ActivityStatus.SUSPENDED
        assert "suspension_reason" in a.metadata

    def test_archive(self):
        a = self._make_activity()
        a.archive()
        assert a.status == ActivityStatus.ARCHIVED

    def test_needs_localization_review_unknown(self):
        a = self._make_activity()
        assert a.needs_localization_review is True

    def test_needs_localization_review_compliant(self):
        a = self._make_activity(localization_status=LocalizationStatus.COMPLIANT)
        assert a.needs_localization_review is False

    def test_has_legal_basis_gap_active_no_basis(self):
        a = self._make_activity()
        a.status = ActivityStatus.ACTIVE
        # metadata has no "has_legal_basis" key → gap
        assert a.has_legal_basis_gap is True

    def test_no_legal_basis_gap_when_draft(self):
        a = self._make_activity()
        # DRAFT status → gap check doesn't apply
        assert a.has_legal_basis_gap is False


class TestDataSubjectRequest:
    def _make_dsr(self, **kwargs) -> DataSubjectRequest:
        defaults = dict(
            tenant_id=uuid4(),
            request_type="ACCESS",
            subject_identifier="user@example.com",
            due_at=datetime.now(UTC) + timedelta(days=30),
        )
        defaults.update(kwargs)
        return DataSubjectRequest(**defaults)

    def test_default_status_is_open(self):
        dsr = self._make_dsr()
        assert dsr.status == DSRStatus.OPEN

    def test_is_overdue_past_deadline(self):
        dsr = self._make_dsr(due_at=datetime.now(UTC) - timedelta(days=1))
        assert dsr.is_overdue is True

    def test_is_not_overdue_future_deadline(self):
        dsr = self._make_dsr(due_at=datetime.now(UTC) + timedelta(days=10))
        assert dsr.is_overdue is False

    def test_days_remaining(self):
        dsr = self._make_dsr(due_at=datetime.now(UTC) + timedelta(days=15))
        # Allow ±1 for timing
        assert 14 <= dsr.days_remaining <= 15

    def test_assign(self):
        dsr = self._make_dsr()
        user = uuid4()
        dsr.assign(user)
        assert dsr.status == DSRStatus.ASSIGNED
        assert dsr.assigned_user_id == user

    def test_complete(self):
        dsr = self._make_dsr()
        dsr.complete()
        assert dsr.status == DSRStatus.COMPLETED
        assert dsr.completed_at is not None

    def test_completed_dsr_not_overdue(self):
        dsr = self._make_dsr(due_at=datetime.now(UTC) - timedelta(days=5))
        dsr.complete()
        assert dsr.is_overdue is False

    def test_respond(self):
        dsr = self._make_dsr()
        dsr.start_work()
        dsr.respond({"text": "Your data has been exported."})
        assert dsr.status == DSRStatus.RESPONDED
        assert dsr.response_payload["text"] == "Your data has been exported."

