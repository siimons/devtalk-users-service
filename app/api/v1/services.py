import json
from fastapi import HTTPException, status

from app.core.database import Database
from app.api.cache.memcached_manager import CacheManager
from app.api.v1.crud import create_user, get_user_by_id

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

    async def get_user(self, db: Database, cache: CacheManager, user_id: int) -> dict:
        """
        Получение информации о пользователе по его ID.
        """
        cache_key = f"user:{user_id}"
        
        try:
            cached_user = await cache.get(cache_key)
            if cached_user:
                logger.info(f"Пользователь {user_id} найден в кэше.")
                return json.loads(cached_user)

            logger.info(f"Запрос данных пользователя с ID {user_id} из БД.")
            user = await get_user_by_id(db, user_id)

            await cache.set(cache_key, json.dumps(user), expire=600)
            logger.success(f"Данные пользователя {user_id} закэшированы на 10 минут.")
            
            return user
        except UserNotFoundException:
            raise user_not_found_exception(user_id)
        except Exception as e:
            logger.error(f"Неизвестная ошибка при получении данных пользователя с ID {user_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Внутренняя ошибка сервера при получении данных пользователя."
            )