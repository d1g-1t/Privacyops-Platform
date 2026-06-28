from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.domain.entities.data_subject_request import DataSubjectRequest
from src.domain.value_objects.dsr_status import DSRStatus


class DSRDomainService:
    @staticmethod
    def create_with_sla(
        *,
        tenant_id: UUID,
        request_type: str,
        subject_identifier: str,
        sla_days: int = 30,
    ) -> DataSubjectRequest:
        now = datetime.now(UTC)
        return DataSubjectRequest(
            tenant_id=tenant_id,
            request_type=request_type,
            subject_identifier=subject_identifier,
            due_at=now + timedelta(days=sla_days),
            submitted_at=now,
        )

    @staticmethod
    def classify_urgency(dsr: DataSubjectRequest) -> str:
        if dsr.is_overdue:
            return "OVERDUE"
        if dsr.days_remaining <= 3:
            return "URGENT"
        if dsr.days_remaining <= 7:
            return "WARNING"
        return "NORMAL"

    @staticmethod
    def can_transition(dsr: DataSubjectRequest, target: DSRStatus) -> bool:
        transitions: dict[DSRStatus, set[DSRStatus]] = {
            DSRStatus.OPEN: {DSRStatus.ASSIGNED, DSRStatus.REJECTED},
            DSRStatus.ASSIGNED: {DSRStatus.IN_PROGRESS, DSRStatus.REJECTED},
            DSRStatus.IN_PROGRESS: {DSRStatus.RESPONDED, DSRStatus.REJECTED},
            DSRStatus.RESPONDED: {DSRStatus.COMPLETED},
        }
        return target in transitions.get(dsr.status, set())
