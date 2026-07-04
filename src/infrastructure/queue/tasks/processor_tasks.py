from __future__ import annotations

import structlog

from src.infrastructure.queue.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(
    name="src.infrastructure.queue.tasks.processor_tasks.processor_review_refresh_task"
)
def processor_review_refresh_task(vendor_id: str) -> dict:
    logger.info("processor_review_refresh", vendor_id=vendor_id)
    return {"vendor_id": vendor_id, "refreshed": True}
