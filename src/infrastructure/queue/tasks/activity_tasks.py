from __future__ import annotations

import structlog

from src.infrastructure.queue.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="src.infrastructure.queue.tasks.activity_tasks.recalculate_activity_risk_task")
def recalculate_activity_risk_task(activity_id: str) -> dict:
    logger.info("recalculate_activity_risk", activity_id=activity_id)

    from src.infrastructure.rules.engine import create_rule_engine

    engine = create_rule_engine()
    context = {
        "activity": {"id": activity_id, "status": "active"},
        "legal_bases": [],
        "localization_assessments": [],
    }
    findings = engine.evaluate(context)
    result = {
        "activity_id": activity_id,
        "findings_count": len(findings),
        "findings": [
            {"rule_id": f.rule_id, "severity": f.severity, "message": f.message}
            for f in findings
        ],
    }
    logger.info("activity_risk_evaluated", **result)
    return result
