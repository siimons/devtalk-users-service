from app.core.database import Database
from app.api.v1.schemas import UserCreate
from app.api.v1.exceptions import UserAlreadyExistsException

from app.core.logging import logger
from app.api.common.utils import hash_password

async def create_user(db: Database, user: UserCreate) -> dict:
    """
    Создание нового пользователя
    """
    query_check = "SELECT id FROM users WHERE email = %s"
    existing_user = await db.fetch(query_check, user.email)
    
    if existing_user:
        logger.error(f"Пользователь с email {user.email} уже существует.")
        raise UserAlreadyExistsException(user.email)

    hashed_password = hash_password(user.password)

    query_create = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """
    try:
        user_id = await db.execute(query_create, user.username, user.email, hashed_password)
        logger.success(f"Пользователь {user.username} успешно создан с ID {user_id}.")
        return {"id": user_id, "username": user.username, "email": user.email}
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {e}")
        raise