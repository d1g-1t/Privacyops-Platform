from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class EvidenceItem:
    tenant_id: UUID
    resource_type: str
    resource_id: UUID
    title: str

    id: UUID = field(default_factory=uuid4)
    file_path: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    created_by: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
