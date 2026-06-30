from __future__ import annotations

import structlog

from src.infrastructure.queue.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(
    name="src.infrastructure.queue.tasks.incident_tasks.incident_timeline_rollup_task"
)
def incident_timeline_rollup_task(incident_id: str) -> dict:
    logger.info("incident_timeline_rollup", incident_id=incident_id)
    return {"incident_id": incident_id, "rolled_up": True}
