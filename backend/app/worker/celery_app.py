from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "memograph",
    broker=settings.redis_broker_url,
    backend=settings.redis_result_url,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="UTC",
    enable_utc=True,

    # Worker behavior
    worker_prefetch_multiplier=1,

    # Task state tracking
    task_track_started=True,

    # Safety limit: 5 minutes
    task_time_limit=300,
)