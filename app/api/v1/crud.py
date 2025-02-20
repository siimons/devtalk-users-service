from app.core.database import Database
from app.api.cache.memcached_manager import CacheManager

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
    UserUpdateException,
    TooManyRequestsException,
    UserDeletionException
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


async def update_user_in_db(db: Database, cache: CacheManager, user_id: int, user_data: UserUpdate) -> dict:
    """
    Обновляет данные пользователя. Требует текущий пароль для изменения email или пароля.
    """
    user_query = "SELECT id, email, password FROM users WHERE id = %s"
    user = await db.fetch(user_query, user_id)

    if not user:
        raise UserNotFoundException(user_id)

    user = user[0]

    brute_force_key = f"brute_force_user_{user_id}"

    if user_data.email or user_data.password:
        if not user_data.current_password:
            raise InvalidCredentialsException()

        failed_attempts = await cache.get(brute_force_key)
        if failed_attempts and int(failed_attempts) >= 5:
            raise TooManyRequestsException(1800)

        if not verify_password(user_data.current_password, user["password"]):
            attempts = await cache.increment(brute_force_key, expire=1800)
            logger.warning(f"Неудачная попытка входа для пользователя {user_id}. Попытка {attempts}/5.")
            raise InvalidCredentialsException()

        await cache.delete(brute_force_key)

    if user_data.email and user_data.email != user["email"]:
        email_check_query = "SELECT id FROM users WHERE email = %s AND id != %s"
        existing_user = await db.fetch(email_check_query, user_data.email, user_id)

        if existing_user:
            raise UserAlreadyExistsException(user_data.email)

    hashed_password = hash_password(user_data.password) if user_data.password else user["password"]

    update_query = """
    UPDATE users 
    SET username = COALESCE(%s, username), 
        email = COALESCE(%s, email), 
        password = %s
    WHERE id = %s
    """
    try:
        await db.execute(update_query, user_data.username, user_data.email, hashed_password, user_id)
        
        logger.success(f"Пользователь с ID {user_id} успешно обновлён.")
        return {
            "id": user_id,
            "username": user_data.username or user["username"],
            "email": user_data.email or user["email"],
        }
    except Exception as e:
        logger.error(f"Неизвестная ошибка при обновлении пользователя с ID {user_id}: {e}")
        raise UserUpdateException(user_id)