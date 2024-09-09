import aiomysql
from fastapi import HTTPException
from datetime import datetime

# Импорт функции для получения пула соединений
from src.utils import get_db_pool

# Функция для добавления нового пользователя в базу данных 
async def add_user(username: str, email: str, password: str) -> dict:
    pool = await get_db_pool()  # Получаем пул соединений
    connection = None
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                # Начало транзакции
                await connection.begin()

                # Вставка нового пользователя
                insert_user_query = """
                INSERT INTO users (username, email, password_hash, created_at)
                VALUES (%s, %s, %s, %s)
                """
                created_at = datetime.now()
                await cursor.execute(insert_user_query, (username, email, password, created_at))

                # Получение ID вставленного пользователя
                user_id = cursor.lastrowid

                # Фиксируем все изменения
                await connection.commit()

                return {'message': 'Пользователь успешно добавлен!', 'user_id': user_id}

    except Exception as e:  # Обработка любых исключений
        if connection:
            await connection.rollback()  # Откатываем транзакцию в случае ошибки
        raise HTTPException(status_code=500, detail=f'Ошибка базы данных: {str(e)}')

    finally:
        pool.close()  # Закрываем пул соединений
        await pool.wait_closed()  # Ждем, пока пул закроется
