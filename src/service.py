from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime

from src.utils import get_db_pool

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
'''Контекст для хеширования паролей с помощью bcrypt'''

async def add_user(username: str, email: str, password: str) -> dict:
    pool = await get_db_pool() 
    connection = None
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:

                await connection.begin()
                
                password_hash = pwd_context.hash(password)

                insert_user_query = """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
                """

                await cursor.execute(insert_user_query, (username, email, password_hash))

                user_id = cursor.lastrowid

                await connection.commit()

                return {'message': 'Пользователь успешно добавлен!', 'user_id': user_id}

    except Exception as e:
        if connection:
            await connection.rollback()
        raise HTTPException(status_code=500, detail=f'Ошибка базы данных: {str(e)}')

    finally:
        pool.close()
        await pool.wait_closed()       
'''Функция для добавления нового пользователя в базу данных '''

async def get_user_by_email(email: str) -> dict:
    pool = await get_db_pool()
    connection = None
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:

                select_user_query = """
                SELECT id, username, email, password_hash, created_at
                FROM users
                WHERE email = %s
                """
                await cursor.execute(select_user_query, (email,))
                user = await cursor.fetchone()

                if not user:
                    raise HTTPException(status_code=404, detail='Пользователь не найден')

                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'password_hash': user[3],
                    'created_at': user[4],
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка базы данных: {str(e)}')

    finally:
        pool.close()
        await pool.wait_closed()

async def verify_password(email: str, password: str) -> bool:

    user = await get_user_by_email(email)

    if pwd_context.verify(password, user['password_hash']):
        return {'message': 'Password is valid'}
    else:
        return {'message': 'Invalid password'}   
'''Функция для хеширования паролей'''

async def get_user_info(user_id: int = None, username: str = None, email: str = None) -> dict:
    pool = await get_db_pool()
    connection = None
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                
                if user_id:
                    query = "SELECT id, username, email, is_active, created_at FROM users WHERE id = %s"
                    await cursor.execute(query, (user_id,))
                elif username:
                    query = "SELECT id, username, email, is_active, created_at FROM users WHERE username = %s"
                    await cursor.execute(query, (username,))
                elif email:
                    query = "SELECT id, username, email, is_active, created_at FROM users WHERE email = %s"
                    await cursor.execute(query, (email,))
                else:
                    raise HTTPException(status_code=400, detail="Необходимо указать id, username или email.")

                user = await cursor.fetchone()

                if not user:
                    raise HTTPException(status_code=404, detail="Пользователь не найден.")

                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'is_active': user[3],
                    'created_at': user[4]
                    }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    finally:
        if connection:
            pool.close()
            await pool.wait_closed()
'''Фнкция для вывода информации о пользователе'''

async def update_user_info(user_id: int, username: str = None, email: str = None, password: str = None) -> dict:
    pool = await get_db_pool()

    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await connection.begin()

                update_fields = []
                update_values = []

                if username:
                    update_fields.append("username = %s")
                    update_values.append(username)

                if email:
                    update_fields.append("email = %s")
                    update_values.append(email)

                if password:
                    hashed_password = pwd_context.hash(password)
                    update_fields.append("password_hash = %s")
                    update_values.append(hashed_password)

                if not update_fields:
                    raise HTTPException(status_code=400, detail="Нет данных для обновления")

                update_values.append(user_id)

                update_query = f"""
                UPDATE users
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

                await cursor.execute(update_query, tuple(update_values))

                await connection.commit()

                return {'message': 'Данные пользователя успешно обновлены!', 'user_id': user_id}

    except Exception as e:
        if connection:
            await connection.rollback()
        raise HTTPException(status_code=500, detail=f'Ошибка базы данных: {str(e)}')

    finally:
        pool.close()
        await pool.wait_closed()
'''Функция для обновления данных пользователя'''