import os
from sys import stdout
from loguru import logger

from app.core.config import settings

LOG_FORMAT_TERMINAL = (
    "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
    "<level>{level}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

LOG_FORMAT_FILE = (
    "{time:YYYY-MM-DD at HH:mm:ss} | {level} | "
    "{name}:{function}:{line} - {message}"
)

def configure_logger():
    """
    Конфигурирует логгер:
    - Удаляет стандартный логгер
    - Создаёт директорию для логов, если она не существует
    - Настраивает логирование в файл с ротацией и вывод в консоль с цветами
    """
    logger.remove()

    log_dir = os.path.dirname(os.path.abspath(settings.LOG_FILE_PATH))
    if log_dir and not os.path.exists(log_dir):
        logger.debug(f"Creating log directory: {log_dir}")
        os.makedirs(log_dir, exist_ok=True)

    logger.add(
        settings.LOG_FILE_PATH,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        level=settings.LOG_LEVEL,
        format=LOG_FORMAT_FILE,
        backtrace=True,
        diagnose=True
    )

    logger.add(
        stdout,
        level=settings.LOG_LEVEL,
        format=LOG_FORMAT_TERMINAL,
        backtrace=True,
        diagnose=True,
        colorize=True
    )

    logger.info("Logger has been configured successfully.")

configure_logger()
__all__ = ['logger']