from decouple import config
import aiomysql
from aiomysql import Pool


HOST = config('HOST')
DATABASE = config('DATABASE')
USER = config('USER')
PASSWORD = config('PASSWORD')

# Асинхронная функция для создания пула подключений к базе данных
async def get_db_pool() -> Pool:
    pool = await aiomysql.create_pool(
        host=HOST,
        db=DATABASE,
        user=USER,
        password=PASSWORD,
        minsize=1,  # минимальное количество подключений в пуле
        maxsize=10,  # максимальное количество подключений в пуле
    )
    return pool


# Асинхронная функция для получения соединения с базой данных из пула
async def get_db_connection(pool: Pool):
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            yield cursor  # Генератор для работы с подключением

