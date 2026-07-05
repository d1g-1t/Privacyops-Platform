from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class RetentionPolicy:
    tenant_id: UUID
    name: str
    retention_days: int
    description: str

    id: UUID = field(default_factory=uuid4)
    auto_delete: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_indefinite(self) -> bool:
        return self.retention_days <= 0
