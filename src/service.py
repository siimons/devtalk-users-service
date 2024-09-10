from passlib.context import CryptContext
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
                
                password_hash = pwd_context.hash(password)

                # Вставка нового пользователя
                insert_user_query = """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
                """

                await cursor.execute(insert_user_query, (username, email, password_hash))

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

# Инициализация контекста для хеширования паролей с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(email: str) -> dict:
    pool = await get_db_pool()  # Получаем пул соединений
    connection = None
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                # Поиск пользователя по email
                select_user_query = """
                SELECT id, username, email, password_hash, created_at
                FROM users
                WHERE email = %s
                """
                await cursor.execute(select_user_query, (email,))
                user = await cursor.fetchone()

                if not user:
                    raise HTTPException(status_code=404, detail="Пользователь не найден")

                # Возвращаем найденного пользователя
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'password_hash': user[3],
                    'created_at': user[4],
                }

    except Exception as e:  # Обработка любых исключений
        raise HTTPException(status_code=500, detail=f'Ошибка базы данных: {str(e)}')

    finally:
        pool.close()  # Закрываем пул соединений
        await pool.wait_closed()  # Ждем, пока пул закроется


async def verify_password(email: str, password: str) -> bool:
    # Получаем данные пользователя по email
    user = await get_user_by_email(email)

    # Сравниваем введенный пароль с хешем, который хранится в базе
    if pwd_context.verify(password, user['password_hash']):
        return {'message': "Password is valid"}
    else:
        return {'message': "Invalid password"}