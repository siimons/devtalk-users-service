from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

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

@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_celery_logging(logger, *args, **kwargs):
    """Настраивает логирование для Celery."""
    logger.handlers.clear()

    celery_log_path = "logs/celery.log"

    logger.add(
        celery_log_path,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True,
        filter=lambda record: "celery" in record["name"],
    )

    logger.info("Celery logging configured successfully. Logs will be saved to: {}", celery_log_path)

logger.info("Celery application initialized with broker: {}", settings.celery_broker_url)
logger.info("Celery configuration updated successfully")

if settings.TESTING:
    celery.conf.task_always_eager = True
    celery.conf.task_eager_propagates = True
    logger.info("Celery running in testing mode (tasks executed eagerly)")
