import json
from fastapi import HTTPException, status

from app.core.database import Database
from app.api.cache.memcached_manager import CacheManager

from app.api.v1.crud import (
    register_new_user, 
    get_user_by_id, 
    authenticate_user
)

from app.api.v1.schemas import (
    UserRegister,
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
from app.api.common.jwt_manager import create_access_token, create_refresh_token


class UserService:
    async def register_user(self, db: Database, user_data: UserRegister) -> dict:
        """
        Регистрация нового пользователя.
        """
        try:
            logger.info(f"Попытка регистрации пользователя с email: {user_data.email}")
            new_user = await register_new_user(db, user_data)
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

    async def login_user(self, db: Database, email: str, password: str) -> dict:
        """
        Аутентификация пользователя и генерация JWT-токенов.
        """
        try:
            user = await authenticate_user(db, email, password)
            access_token = create_access_token({"sub": user["id"]})
            refresh_token = create_refresh_token({"sub": user["id"]})

            logger.info(f"Пользователь {user['username']} успешно аутентифицирован.")
            return {"access_token": access_token, "refresh_token": refresh_token}

        except InvalidCredentialsException:
            logger.warning(f"Ошибка аутентификации для {email}: неверные учетные данные.")
            raise invalid_credentials_exception()
        except Exception as e:
            logger.error(f"Ошибка при аутентификации: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при входе в систему."
            )
    
    async def get_user(self, db: Database, cache: CacheManager, user: dict) -> dict:
        """
        Получение информации о текущем пользователе.
        """
        user_id = user["id"]
        cache_key = f"user:{user_id}"

        try:
            cached_user = await cache.get(cache_key)
            if cached_user:
                logger.info(f"Пользователь {user_id} найден в кэше.")
                return json.loads(cached_user)

            logger.info(f"Запрос данных пользователя {user_id} из БД.")
            user_data = await get_user_by_id(db, user_id)

            await cache.set(cache_key, json.dumps(user_data), expire=600)
            logger.success(f"Данные пользователя {user_id} закэшированы на 10 минут.")

            return user_data
        except UserNotFoundException:
            raise user_not_found_exception(user_id)
        except Exception as e:
            logger.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Внутренняя ошибка сервера."
            )