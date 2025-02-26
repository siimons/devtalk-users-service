import aiomysql
from typing import List, Optional

from app.core.settings import settings
from app.core.logging import logger


class Database:
    
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Создание пула соединений с базой данных."""
        try:
            logger.info("Подключение к базе данных...")
            logger.info(
                f"Подключение к базе данных: host={settings.MYSQL_HOST}, "
                f"port={settings.MYSQL_PORT}, user={settings.MYSQL_USER}"
            )
            self.pool = await aiomysql.create_pool(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                db=settings.MYSQL_DATABASE,
                autocommit=True,
                maxsize=10
            )
            logger.success("Успешное подключение к базе данных.")
        except Exception as e:
            logger.error(f"Ошибка при подключении к базе данных: {e}")
            raise

    async def close(self):
        """Закрытие соединений с базой данных."""
        try:
            if self.pool:
                logger.info("Закрытие соединений с базой данных...")
                self.pool.close()
                await self.pool.wait_closed()
                logger.success("Соединения с базой данных закрыты.")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединений с базой данных: {e}")

    async def fetch(self, query: str, *args) -> List[dict]:
        """Выполнение запроса, возвращающего результаты (например SELECT)."""
        try:
            logger.info(f"Выполнение запроса: {query} | Аргументы: {args}")
            async with self.pool.acquire() as connection:
                async with connection.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, args)
                    result = await cursor.fetchall()
                    logger.info(f"Запрос выполнен успешно. Получено строк: {len(result)}")
                    return result
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    async def execute(self, query: str, *args) -> Optional[int]:
        """Выполнение запроса без возвращаемых результатов (например INSERT, UPDATE, DELETE)."""
        try:
            logger.info(f"Выполнение запроса: {query} | Аргументы: {args}")
            async with self.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(query, args)
                    lastrowid = cursor.lastrowid
                    logger.info(f"Запрос выполнен успешно. ID последней вставленной записи: {lastrowid}")
                    return lastrowid
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    async def start_transaction(self):
        """Начало транзакции."""
        logger.info("Начало транзакции...")
        async with self.pool.acquire() as connection:
            connection.autocommit(False)
            self._connection = connection

    async def commit_transaction(self):
        """Фиксация транзакции."""
        if hasattr(self, '_connection'):
            logger.info("Фиксация транзакции...")
            await self._connection.commit()
            self._connection.autocommit(True)
            self._connection = None

    async def rollback_transaction(self):
        """Откат транзакции."""
        if hasattr(self, '_connection'):
            logger.info("Откат транзакции...")
            await self._connection.rollback()
            self._connection.autocommit(True)
            self._connection = None