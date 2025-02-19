from app.core.database import Database

from app.api.v1.schemas import (
    UserRegister,
    UserLogin,
    UserUpdate,
    UserDelete
)

from app.api.v1.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserUpdateException
)

from app.core.logging import logger
from app.api.common.hashing import hash_password, verify_password


async def register_new_user(db: Database, user: UserRegister) -> dict:
    """
    Регистрация нового пользователя.
    """
    query_check = "SELECT id FROM users WHERE email = %s"
    existing_user = await db.fetch(query_check, user.email)

    if existing_user:
        raise UserAlreadyExistsException(user.email)

    hashed_password = hash_password(user.password)

    query_insert = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """
    try:
        user_id = await db.execute(query_insert, user.username, user.email, hashed_password)
        logger.success(f"Пользователь {user.username} успешно зарегистрирован (ID: {user_id}).")
        return {"id": user_id, "username": user.username, "email": user.email}
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        raise


async def authenticate_user(db: Database, user_data: UserLogin) -> dict:
    """
    Проверяет, существует ли пользователь с указанными email и паролем.
    """
    query = "SELECT id, username, email, password FROM users WHERE email = %s"
    users = await db.fetch(query, user_data.email)

    if not users:
        raise InvalidCredentialsException()

    user = users[0]
    if not verify_password(user_data.password, user["password"]):
        raise InvalidCredentialsException()

    return {"id": user["id"], "username": user["username"], "email": user["email"]}


async def get_user_by_id(db: Database, user_id: int) -> dict:
    """
    Получение данных пользователя по его ID.
    """
    query = "SELECT id, username, email FROM users WHERE id = %s"
    try:
        users = await db.fetch(query, user_id)
        if not users:
            raise UserNotFoundException(user_id)
        
        user = users[0]
        logger.info(f"Информация о пользователе с ID {user_id} успешно получена.")
        return {"id": user["id"], "username": user["username"], "email": user["email"]}
    except UserNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Неизвестная ошибка при запросе данных пользователя с ID {user_id}: {e}")
        raise


async def update_user_in_db(db: Database, user_id: int, user_data: UserUpdate) -> dict:
    """
    Полностью обновляет данные пользователя (заменяет все поля, кроме пароля, если он не передан).
    """
    user_query = "SELECT id, password FROM users WHERE id = %s"
    user = await db.fetch(user_query, user_id)

    if not user:
        raise UserNotFoundException(user_id)

    email_check_query = "SELECT id FROM users WHERE email = %s AND id != %s"
    existing_user = await db.fetch(email_check_query, user_data.email, user_id)

    if existing_user:
        raise UserAlreadyExistsException(user_data.email)

    hashed_password = hash_password(user_data.password) if user_data.password else user[0]["password"]

    update_query = """
    UPDATE users 
    SET username = %s, email = %s, password = %s
    WHERE id = %s
    """
    try:
        await db.execute(update_query, user_data.username, user_data.email, hashed_password, user_id)
        
        logger.success(f"Пользователь с ID {user_id} успешно обновлён.")
        return {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
        }
    except Exception as e:
        logger.error(f"Неизвестная ошибка при обновлении пользователя с ID {user_id}: {e}")
        raise UserUpdateException(user_id)
    