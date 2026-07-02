from __future__ import annotations

import structlog

from src.infrastructure.queue.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="src.infrastructure.queue.tasks.consent_tasks.consent_expiry_scan_task")
def consent_expiry_scan_task() -> dict:
    logger.info("consent_expiry_scan_started")
    return {"scanned": True, "expiring_count": 0, "withdrawn_count": 0}
