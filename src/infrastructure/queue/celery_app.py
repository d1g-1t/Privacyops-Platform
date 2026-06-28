from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from src.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "privacyops",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "src.infrastructure.queue.tasks.activity_tasks.*": {"queue": "privacy.registry"},
        "src.infrastructure.queue.tasks.dsr_tasks.*": {"queue": "privacy.dsr"},
        "src.infrastructure.queue.tasks.consent_tasks.*": {"queue": "privacy.monitoring"},
        "src.infrastructure.queue.tasks.processor_tasks.*": {"queue": "privacy.monitoring"},
        "src.infrastructure.queue.tasks.incident_tasks.*": {"queue": "privacy.incidents"},
        "src.infrastructure.queue.tasks.analytics_tasks.*": {"queue": "privacy.analytics"},
    },
    beat_schedule={
        "dsr-sla-scan": {
            "task": "src.infrastructure.queue.tasks.dsr_tasks.dsr_sla_scan_task",
            "schedule": crontab(minute="*/30"),
        },
        "consent-expiry-scan": {
            "task": "src.infrastructure.queue.tasks.consent_tasks.consent_expiry_scan_task",
            "schedule": crontab(hour=6, minute=0),
        },
        "analytics-refresh": {
            "task": "src.infrastructure.queue.tasks.analytics_tasks.analytics_refresh_task",
            "schedule": crontab(minute="*/15"),
        },
    },
)

celery_app.autodiscover_tasks(
    [
        "src.infrastructure.queue.tasks.activity_tasks",
        "src.infrastructure.queue.tasks.dsr_tasks",
        "src.infrastructure.queue.tasks.consent_tasks",
        "src.infrastructure.queue.tasks.processor_tasks",
        "src.infrastructure.queue.tasks.incident_tasks",
        "src.infrastructure.queue.tasks.analytics_tasks",
    ]
)
