from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class ConsentTemplate:
    tenant_id: UUID
    name: str
    version: int
    channel: str
    text_body: str

    id: UUID = field(default_factory=uuid4)
    language_code: str = "ru"
    active: bool = True
    checksum: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.checksum:
            self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        content = f"{self.name}:{self.version}:{self.text_body}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def new_version(self, text_body: str) -> ConsentTemplate:
        return ConsentTemplate(
            tenant_id=self.tenant_id,
            name=self.name,
            version=self.version + 1,
            channel=self.channel,
            text_body=text_body,
            language_code=self.language_code,
        )
