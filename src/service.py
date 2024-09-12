from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime

from src.utils import get_db_pool
from src.exceptions import CommentNotFoundException

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

async def add_comment(user_id: int, article_id: int, content: str) -> dict:
    pool = await get_db_pool()
     
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await connection.begin()
                
                insert_comment_query = """
                INSERT INTO comments (user_id, article_id, content)
                VALUES (%s, %s, %s)
                """

                await cursor.execute(insert_comment_query, (user_id, article_id, content))

                comment_id = cursor.lastrowid

                await connection.commit()

                return {'message': 'Комментарий успешно добавлен!', 'comment_id': comment_id}

    except Exception as e:
        if connection:
            await connection.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении комментария: {str(e)}")

    finally:
        pool.close()
        await pool.wait_closed()
'''Функция для сохранения комментария в базу данных'''

async def delete_comment(comment_id: int, user_id: int) -> dict:
    pool = await get_db_pool()

    async with pool.acquire() as connection:
        try:
            async with connection.cursor() as cursor:
                select_comment_query = "SELECT id FROM comments WHERE id = %s AND user_id = %s"
                await cursor.execute(select_comment_query, (comment_id, user_id))
                comment = await cursor.fetchone()

                if not comment:
                    raise CommentNotFoundException(comment_id)

                delete_comment_query = "DELETE FROM comments WHERE id = %s AND user_id = %s"
                await cursor.execute(delete_comment_query, (comment_id, user_id))

                await connection.commit()

                return {"message": f"Комментарий с ID {comment_id} успешно удален"}

        except Exception as e:
            await connection.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении комментария: {str(e)}")

        finally:
            pool.close()
            await pool.wait_closed()
'''Функция для удаления комментария'''