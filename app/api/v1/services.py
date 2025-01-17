from fastapi import HTTPException, status

from app.core.database import Database
from app.api.v1.crud import create_user

from app.api.v1.schemas import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserDelete,
    User,
)

from app.api.v1.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    user_not_found_exception,
    user_already_exists_exception,
    invalid_credentials_exception,
)

from app.core.logging import logger


class UserService:
    async def register_user(self, db: Database, user_data: UserCreate) -> dict:
        """
        Регистрация нового пользователя.
        """
        try:
            logger.info(f"Попытка регистрации пользователя с email: {user_data.email}")
            new_user = await create_user(db, user_data)
            logger.success(f"Пользователь {new_user['username']} успешно зарегистрирован.")
            return new_user
        except UserAlreadyExistsException:
            logger.error(f"Пользователь с email {user_data.email} уже существует.")
            raise user_already_exists_exception(user_data.email)
        except Exception as e:
            logger.error(f"Неизвестная ошибка при регистрации пользователя: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при регистрации пользователя."
            )