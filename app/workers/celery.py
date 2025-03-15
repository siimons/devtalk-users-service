from celery import Celery

from app.core.settings import settings
from app.core.logging import logger

celery = Celery(
    "dev_talk_workers",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.tasks.send_email",
        "app.workers.tasks.delete_account",
    ],
)

celery.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    worker_hijack_root_logger=False,
)

if settings.TESTING:
    celery.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

logger.info("Celery has been successfully configured.")