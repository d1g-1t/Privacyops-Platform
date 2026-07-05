from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class ProcessorVendor:
    tenant_id: UUID
    legal_name: str
    service_type: str

    id: UUID = field(default_factory=uuid4)
    inn: str | None = None
    hosts_personal_data: bool = False
    subprocessors_used: bool = False
    status: str = "DRAFT"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def approve(self) -> None:
        self.status = "ACTIVE"

    def reject(self, reason: str) -> None:
        self.status = "REJECTED"
        self.metadata["rejection_reason"] = reason

    def suspend(self, reason: str) -> None:
        self.status = "SUSPENDED"
        self.metadata["suspension_reason"] = reason
