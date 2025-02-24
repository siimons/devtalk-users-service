from fastapi import HTTPException

from app.api.v1.repositories import UserRepository
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

from app.api.common.hashing import hash_password, verify_password
from app.api.common.jwt_manager import create_access_token, create_refresh_token

from app.core.logging import logger


class UserService:
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_data: UserRegister) -> dict:
        """Регистрация нового пользователя."""
        try:
            logger.info(f"Попытка регистрации пользователя с email: {user_data.email}")
            if await self.user_repo.check_email_exists(user_data.email):
                raise UserAlreadyExistsException(user_data.email)

            hashed_password = hash_password(user_data.password)
            registered_user = await self.user_repo.create_user(
                user_data.username, user_data.email, hashed_password
            )
            logger.success(f"Пользователь {registered_user['username']} успешно зарегистрирован.")
            return registered_user
        except UserAlreadyExistsException as e:
            logger.error(f"Пользователь с email {user_data.email} уже существует.")
            raise e.to_http()
        except Exception as e:
            logger.error(f"Неизвестная ошибка при регистрации пользователя: {e}")
            raise HTTPException(
                status_code=500, detail="Ошибка при регистрации пользователя."
            )

    async def login_user(self, user_data: UserLogin) -> dict:
        """Аутентификация пользователя и генерация JWT-токенов."""
        try:
            user = await self.user_repo.get_user_by_email(user_data.email)
            if not user or not verify_password(user_data.password, user["password"]):
                raise InvalidCredentialsException()

            access_token = create_access_token({"sub": user["id"]})
            refresh_token = create_refresh_token({"sub": user["id"]})

            logger.info(f"Пользователь {user['username']} успешно аутентифицирован.")
            return {"access_token": access_token, "refresh_token": refresh_token}
        except InvalidCredentialsException as e:
            logger.warning(f"Ошибка аутентификации для {user_data.email}: неверные учетные данные.")
            raise e.to_http()
        except Exception as e:
            logger.error(f"Ошибка при аутентификации: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при входе в систему.")

    async def get_user(self, user_id: int) -> dict:
        """Получает данные пользователя по ID."""
        try:
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id)
            return user
        except UserNotFoundException as e:
            logger.error(f"Пользователь с ID {user_id} не найден.")
            raise e.to_http()
        except Exception as e:
            logger.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера.")

    async def update_user(self, user_id: int, user_data: UserUpdate, cache: CacheManager) -> dict:
        """Обновляет данные пользователя."""
        try:
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id)

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
                if await self.user_repo.check_email_exists(user_data.email, exclude_user_id=user_id):
                    raise UserAlreadyExistsException(user_data.email)

            hashed_password = hash_password(user_data.password) if user_data.password else None
            updated_user = await self.user_repo.update_user(
                user_id, user_data.username, user_data.email, hashed_password
            )
            logger.success(f"Пользователь с ID {user_id} успешно обновлён.")
            return updated_user
        except (UserNotFoundException, UserAlreadyExistsException, InvalidCredentialsException, TooManyRequestsException) as e:
            raise e.to_http()
        except Exception as e:
            logger.error(f"Ошибка при обновлении пользователя с ID {user_id}: {e}")
            raise UserUpdateException(user_id).to_http()