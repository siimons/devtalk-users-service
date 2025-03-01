from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Конфигурационный класс приложения."""

    # Логирование
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_LEVEL: str = "INFO"
    LOG_ROTATION: str = "100 MB"
    LOG_RETENTION: str = "5 days"

    # MySQL
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    # Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Elastic Email
    SMTP_HOST: str = "smtp.elasticemail.com"
    SMTP_PORT: int = 2525
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str = "no-reply@dev-talk.com"
    EMAIL_FROM_NAME: str = "DevTalk Support"

    # Тестирование
    TESTING: bool = False

    model_config = ConfigDict(env_file=".env", extra="ignore")

    @property
    def celery_broker_url(self) -> str:
        """
        Формирует URL брокера Celery.

        Returns:
            str: Адрес брокера для передачи задач Celery.
        """
        password = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password}{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    @property
    def celery_result_backend(self) -> str:
        """
        Формирует URL бэкенда результатов Celery.

        Returns:
            str: Адрес хранилища результатов выполнения задач Celery.
        """
        password = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password}{self.REDIS_HOST}:{self.REDIS_PORT}/2"


settings = Settings()
