import redis.asyncio as redis
from typing import Optional

from app.core.settings import settings
from app.core.logging import logger


class RedisManager:
    """
    Менеджер для работы с Redis.

    Attributes:
        client (Optional[redis.Redis]): Клиент Redis, используемый для операций.
    """

    def __init__(self):
        """
        Инициализирует RedisManager.

        Args:
            client (Optional[redis.Redis]): Клиент Redis, используемый для операций.
        """
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Устанавливает соединение с Redis."""
        try:
            logger.info(f"Подключение к Redis: host={settings.REDIS_HOST}, port={settings.REDIS_PORT}")
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
            )
            await self.client.ping()
            logger.success("Успешное подключение к Redis.")
        except Exception as e:
            logger.error(f"Ошибка при подключении к Redis: {e}")
            raise

    async def close(self):
        """Закрывает соединение с Redis."""
        if self.client:
            try:
                logger.info("Закрытие соединения с Redis...")
                await self.client.aclose()
                logger.success("Соединение с Redis закрыто.")
            except Exception as e:
                logger.error(f"Ошибка при закрытии Redis: {e}")

    async def clear_cache(self):
        """Очищает весь кэш Redis."""
        if self.client:
            try:
                await self.client.flushdb()
                logger.info("Кэш Redis успешно очищен.")
            except Exception as e:
                logger.error(f"Ошибка при очистке кэша Redis: {e}")

    async def get(self, key: str) -> Optional[str]:
        """
        Получает значение из Redis по ключу.

        Args:
            key (str): Ключ в хранилище.

        Returns:
            Optional[str]: Значение, если ключ найден, иначе None.
        """
        try:
            value = await self.client.get(key)
            if value is not None:
                logger.info(f"Ключ {key} найден в Redis.")
                return value
            logger.info(f"Ключ {key} не найден в Redis.")
        except Exception as e:
            logger.error(f"Ошибка при получении ключа {key} из Redis: {e}")
            return None

    async def set(self, key: str, value: str, expire: int = 3600):
        """
        Сохраняет значение в Redis.

        Args:
            key (str): Ключ.
            value (str): Значение.
            expire (int, optional): Время жизни в секундах. По умолчанию 3600.
        """
        try:
            await self.client.set(key, value, ex=expire)
            logger.info(f"Ключ {key} сохранён в Redis (TTL={expire} сек.).")
        except Exception as e:
            logger.error(f"Ошибка при сохранении ключа {key} в Redis: {e}")

    async def delete(self, key: str):
        """
        Удаляет ключ из Redis.

        Args:
            key (str): Ключ.
        """
        try:
            await self.client.delete(key)
            logger.info(f"Ключ {key} удалён из Redis.")
        except Exception as e:
            logger.error(f"Ошибка при удалении ключа {key} из Redis: {e}")

    async def increment(self, key: str, expire: int = 1800) -> int:
        """
        Увеличивает значение ключа. Если ключа нет, создаёт его со значением 1.

        Args:
            key (str): Ключ.
            expire (int, optional): TTL в секундах. По умолчанию 1800.

        Returns:
            int: Новое значение ключа.
        """
        try:
            value = await self.client.incr(key)
            await self.client.expire(key, expire)
            logger.info(f"Значение ключа {key} увеличено до {value}.")
            return value
        except Exception as e:
            logger.error(f"Ошибка при увеличении значения ключа {key}: {e}")
            return 0
    