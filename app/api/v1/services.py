import json
from fastapi import HTTPException

from app.api.v1.repositories import UserRepository
from app.api.storage.redis import RedisManager
from app.api.common.tokens import TokenService

from app.api.v1.schemas import (
    UserRegister,
    UserLogin,
    UserUpdate,
    UserDelete,
    UserRestore,
)

from app.api.v1.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserUpdateException,
    TooManyRequestsException,
    UserDeletionException,
)

from app.api.common.hashing import hash_value, verify_value
from app.api.common.jwt_manager import create_access_token, create_refresh_token

from app.workers.tasks.send_email import send_restoration_email
from app.workers.tasks.delete_account import delete_account_permanently

from app.core.settings import settings
from app.core.logging import logger


class UserService:
    """
    Сервис для управления пользователями.

    Attributes:
        user_repo (UserRepository): Репозиторий для работы с базой данных пользователей.
        cache (RedisManager): Менеджер для работы с Redis.
    """

    def __init__(self, user_repo: UserRepository, cache: RedisManager):
        """
        Инициализирует UserService.

        Args:
            user_repo (UserRepository): Репозиторий для работы с базой данных пользователей.
            cache (RedisManager): Менеджер для работы с Redis.
        """
        self.user_repo = user_repo
        self.cache = cache

    async def register_user(self, user_data: UserRegister) -> dict:
        """
        Регистрирует нового пользователя.

        Args:
            user_data (UserRegister): Данные для регистрации пользователя.

        Returns:
            dict: Данные зарегистрированного пользователя.

        Raises:
            HTTPException: Если пользователь с таким email уже существует или произошла ошибка.
        """
        try:
            logger.info(f"Попытка регистрации пользователя с email: {user_data.email}")
            if await self.user_repo.check_email_exists(user_data.email):
                raise UserAlreadyExistsException(user_data.email)

            hashed_password = hash_value(user_data.password)
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
        """
        Аутентифицирует пользователя и генерирует JWT-токены.

        Args:
            user_data (UserLogin): Данные для входа пользователя.

        Returns:
            dict: JWT-токены (access и refresh).

        Raises:
            HTTPException: Если учетные данные неверны или произошла ошибка.
        """
        try:
            user = await self.user_repo.get_user_by_email(user_data.email)
            if not user or not verify_value(user_data.password, user["password"]):
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
        """
        Получает данные пользователя по ID.

        Args:
            user_id (int): ID пользователя.

        Returns:
            dict: Данные пользователя.

        Raises:
            HTTPException: Если пользователь не найден или произошла ошибка.
        """
        cache_key = f"user:{user_id}"

        try:
            cached_user = await self.cache.get(cache_key)
            if cached_user:
                logger.info(f"Данные пользователя {user_id} получены из кэша")
                return json.loads(cached_user)

            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id)

            await self.cache.set(cache_key, json.dumps(user), expire=3600)
            logger.info(f"Данные пользователя {user_id} сохранены в кэш")

            return user
        except UserNotFoundException as e:
            logger.error(f"Пользователь с ID {user_id} не найден.")
            raise e.to_http()
        except Exception as e:
            logger.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера.")

    async def update_user(self, user_id: int, user_data: UserUpdate) -> dict:
        """
        Обновляет данные пользователя.

        Args:
            user_id (int): ID пользователя.
            user_data (UserUpdate): Данные для обновления.

        Returns:
            dict: Обновлённые данные пользователя.

        Raises:
            HTTPException: Если пользователь не найден, email уже занят, неверный пароль,
                        превышено количество попыток или произошла ошибка.
        """
        try:
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id)

            brute_force_key = f"brute_force_update:{user_id}"
            if user_data.email or user_data.password:
                if not user_data.current_password:
                    raise InvalidCredentialsException()

                attempts = await self.cache.get(brute_force_key)
                if attempts and int(attempts) >= settings.BRUTE_FORCE_MAX_ATTEMPTS:
                    raise TooManyRequestsException(settings.BRUTE_FORCE_BLOCK_TIME)

                if not verify_value(user_data.current_password, user["password"]):
                    await self.cache.increment(brute_force_key, expire=settings.BRUTE_FORCE_BLOCK_TIME)
                    logger.warning(
                        f"Неудачная попытка входа для пользователя {user_id}.\n"
                        f"Попытка {attempts}/{settings.BRUTE_FORCE_MAX_ATTEMPTS}."
                    )
                    raise InvalidCredentialsException()

                await self.cache.delete(brute_force_key)

            if user_data.email and user_data.email != user["email"]:
                if await self.user_repo.check_email_exists(user_data.email, exclude_user_id=user_id):
                    raise UserAlreadyExistsException(user_data.email)

            hashed_password = hash_value(user_data.password) if user_data.password else user["password"]
            updated_user = await self.user_repo.update_user_in_db(
                user_id, user_data.username, user_data.email, hashed_password
            )
            logger.success(f"Пользователь с ID {user_id} успешно обновлён.")
            return updated_user
        except (
            UserNotFoundException,
            UserAlreadyExistsException,
            InvalidCredentialsException,
            TooManyRequestsException,
        ) as e:
            raise e.to_http()
        except Exception as e:
            logger.error(f"Ошибка при обновлении пользователя с ID {user_id}: {e}")
            raise UserUpdateException(user_id).to_http()

    async def delete_user(self, user_id: int, user_data: UserDelete) -> bool:
        """
        Удаляет аккаунт пользователя.

        Args:
            user_id (int): ID пользователя.
            user_data (UserDelete): Данные для удаления аккаунта.

        Returns:
            bool: True, если пользователь успешно помечен как удалённый.

        Raises:
            HTTPException: Если пользователь не найден, пароль неверен,
                        превышено количество попыток или произошла ошибка.
        """
        try:
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id)

            brute_force_key = f"brute_force_delete:{user_id}"
            attempts = await self.cache.get(brute_force_key)
            if attempts and int(attempts) >= settings.BRUTE_FORCE_MAX_ATTEMPTS:
                raise TooManyRequestsException(settings.BRUTE_FORCE_BLOCK_TIME)

            if not verify_value(user_data.current_password, user["password"]):
                await self.cache.increment(brute_force_key, expire=settings.BRUTE_FORCE_BLOCK_TIME)
                logger.warning(
                    f"Неудачная попытка удаления для пользователя {user_id}.\n"
                    f"Попытка {attempts}/{settings.BRUTE_FORCE_MAX_ATTEMPTS}."
                )
                raise InvalidCredentialsException()

            restoration_token = TokenService.generate_restoration_token()
            hashed_token = hash_value(restoration_token)

            await self.user_repo.soft_delete_user(user_id, hashed_token)

            delete_account_permanently.apply_async(
                args=[user_id],
                countdown=settings.RESTORATION_TOKEN_EXPIRE_DAYS * 86400,
            )
            send_restoration_email.delay(user["email"], restoration_token)

            logger.success(
                f"Пользователь {user_id} помечен как удалённый. "
                f"Токен восстановления отправлен на email."
            )
            return True
        except (
            UserNotFoundException,
            InvalidCredentialsException,
            TooManyRequestsException,
        ) as e:
            raise e.to_http()
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя {user_id}: {e}")
            raise UserDeletionException(user_id).to_http()