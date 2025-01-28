import aiomcache

from app.core.logging import logger
from app.core.config import settings


class CacheManager:
    """
    Класс для работы с кэшированием данных через Memcached.
    """

    def __init__(self):
        self.client = None

    async def connect(self):
        """
        Подключение к Memcached.
        """
        try:
            logger.info(f"Подключение к Memcached: host={settings.MEMCACHED_HOST}, port={settings.MEMCACHED_PORT}")
            self.client = aiomcache.Client(
                settings.MEMCACHED_HOST,
                settings.MEMCACHED_PORT
            )
            logger.success("Успешное подключение к Memcached.")
        except Exception as e:
            logger.error(f"Ошибка при подключении к Memcached: {e}")
            raise

    async def close(self):
        """
        Закрытие соединения с Memcached.
        """
        try:
            if self.client:
                logger.info("Закрытие соединения с Memcached...")
                await self.client.close()
                logger.success("Соединение с Memcached закрыто.")
        except Exception as e:
            logger.error(f"Ошибка при закрытии Memcached: {e}")

    async def get(self, key: str):
        """
        Получить значение из кэша.
        """
        try:
            value = await self.client.get(key.encode("utf-8"))
            if value:
                logger.info(f"Ключ {key} найден в кэше.")
                return value.decode("utf-8")
            logger.info(f"Ключ {key} не найден в кэше.")
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении ключа {key} из кэша: {e}")
            return None

    async def set(self, key: str, value: str, expire: int = 3600):
        """
        Установить значение в кэш.
        """
        try:
            await self.client.set(key.encode("utf-8"), value.encode("utf-8"), exptime=expire)
            logger.info(f"Ключ {key} сохранён в кэше с временем истечения {expire} секунд.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении ключа {key} в кэш: {e}")

    async def delete(self, key: str):
        """
        Удалить значение из кэша.
        """
        try:
            await self.client.delete(key.encode("utf-8"))
            logger.info(f"Ключ {key} удалён из кэша.")
        except Exception as e:
            logger.error(f"Ошибка при удалении ключа {key} из кэша: {e}")
