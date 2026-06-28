from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.value_objects.dsr_status import DSRStatus


@dataclass
class DataSubjectRequest:
    tenant_id: UUID
    request_type: str
    subject_identifier: str
    due_at: datetime

    id: UUID = field(default_factory=uuid4)
    status: DSRStatus = DSRStatus.OPEN
    submitted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    assigned_user_id: UUID | None = None
    response_payload: dict[str, Any] = field(default_factory=dict)
    evidence_payload: dict[str, Any] = field(default_factory=dict)
    completed_at: datetime | None = None

    def assign(self, user_id: UUID) -> None:
        self.assigned_user_id = user_id
        self.status = DSRStatus.ASSIGNED

    def start_work(self) -> None:
        if self.status not in (DSRStatus.OPEN, DSRStatus.ASSIGNED):
            raise ValueError(f"Cannot start work on DSR in status {self.status}")
        self.status = DSRStatus.IN_PROGRESS

    def respond(self, payload: dict[str, Any]) -> None:
        self.response_payload = payload
        self.status = DSRStatus.RESPONDED

    def complete(self, evidence: dict[str, Any] | None = None) -> None:
        self.status = DSRStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        if evidence:
            self.evidence_payload = evidence

    @property
    def is_overdue(self) -> bool:
        return self.status not in (DSRStatus.COMPLETED, DSRStatus.REJECTED) and (
            datetime.now(UTC) > self.due_at
        )

    @property
    def days_remaining(self) -> int:
        if self.status in (DSRStatus.COMPLETED, DSRStatus.REJECTED):
            return 0
        delta = self.due_at - datetime.now(UTC)
        return max(0, delta.days)
