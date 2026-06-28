from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.value_objects.activity_status import ActivityStatus
from src.domain.value_objects.localization_status import LocalizationStatus


@dataclass
class DataProcessingActivity:
    tenant_id: UUID
    title: str
    purpose: str
    system_name: str
    operator_role: str

    id: UUID = field(default_factory=uuid4)
    owner_user_id: UUID | None = None
    status: ActivityStatus = ActivityStatus.DRAFT
    localization_status: LocalizationStatus = LocalizationStatus.UNKNOWN
    retention_policy_name: str | None = None
    cross_border_transfer: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def activate(self) -> None:
        if self.status not in (ActivityStatus.DRAFT, ActivityStatus.UNDER_REVIEW):
            raise ValueError(f"Cannot activate activity in status {self.status}")
        self.status = ActivityStatus.ACTIVE
        self.updated_at = datetime.now(UTC)

    def suspend(self, reason: str) -> None:
        self.status = ActivityStatus.SUSPENDED
        self.metadata["suspension_reason"] = reason
        self.updated_at = datetime.now(UTC)

    def archive(self) -> None:
        self.status = ActivityStatus.ARCHIVED
        self.updated_at = datetime.now(UTC)

    @property
    def has_legal_basis_gap(self) -> bool:
        return self.status == ActivityStatus.ACTIVE and not self.metadata.get("has_legal_basis")

    @property
    def needs_localization_review(self) -> bool:
        return self.localization_status in (
            LocalizationStatus.UNKNOWN,
            LocalizationStatus.NON_COMPLIANT,
        )
