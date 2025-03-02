from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.settings import settings


def get_rate_limiter() -> Limiter:
    """
    Возвращает объект Limiter с настроенным хранилищем Redis.

    Returns:
        Limiter: Объект Limiter для ограничения запросов.
    """
    redis_password = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
    storage_uri = f"redis://{redis_password}{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=storage_uri,
    )
    return limiter
