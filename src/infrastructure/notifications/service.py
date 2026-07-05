from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class NotificationService:

    async def send(self, *, channel: str, recipient: str, subject: str, body: str) -> None:
        logger.info(
            "notification_sent",
            channel=channel,
            recipient=recipient,
            subject=subject,
        )
