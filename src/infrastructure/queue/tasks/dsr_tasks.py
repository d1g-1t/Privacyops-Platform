from __future__ import annotations

import structlog

from src.infrastructure.queue.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="src.infrastructure.queue.tasks.dsr_tasks.dsr_sla_scan_task")
def dsr_sla_scan_task() -> dict:
    logger.info("dsr_sla_scan_started")
    return {"scanned": True, "overdue_count": 0, "near_overdue_count": 0}
