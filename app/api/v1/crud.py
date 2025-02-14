from app.core.database import Database
from app.api.v1.schemas import UserRegister

from app.api.v1.exceptions import (
    UserAlreadyExistsException, 
    UserNotFoundException, 
    InvalidCredentialsException
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
        logger.error(f"Пользователь с email {user.email} уже существует.")
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


async def authenticate_user(db: Database, email: str, password: str) -> dict:
    """
    Проверяет, существует ли пользователь с указанными email и паролем.
    """
    query = "SELECT id, username, email, password FROM users WHERE email = %s"
    users = await db.fetch(query, email)

    if not users:
        raise InvalidCredentialsException()

    user = users[0]
    if not verify_password(password, user["password"]):
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
            logger.error(f"Пользователь с ID {user_id} не найден.")
            raise UserNotFoundException(user_id)
        
        user = users[0]
        logger.info(f"Информация о пользователе с ID {user_id} успешно получена.")
        return {"id": user["id"], "username": user["username"], "email": user["email"]}
    except UserNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Неизвестная ошибка при запросе данных пользователя с ID {user_id}: {e}")
        raise