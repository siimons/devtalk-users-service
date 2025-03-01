from typing import Optional

from app.api.storage.database import Database


class UserRepository:
    """
    Репозиторий для работы с пользователями в базе данных.

    Attributes:
        db (Database): Экземпляр класса для работы с базой данных.
    """
    
    def __init__(self, db: Database):
        """
        Инициализирует UserRepository.

        Args:
            db (Database): Объект базы данных.
        """
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """
        Возвращает данные активного пользователя по email.

        Args:
            email (str): Email пользователя.

        Returns:
            Optional[dict]: Данные пользователя или None, если пользователь не найден или удалён.
        """
        query = """
        SELECT id, username, email, password
        FROM users
        WHERE email = %s
          AND deleted_at IS NULL
        """
        users = await self.db.fetch(query, email)
        return users[0] if users else None

    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """
        Возвращает данные активного пользователя по ID.

        Args:
            user_id (int): Уникальный идентификатор пользователя.

        Returns:
            Optional[dict]: Данные пользователя или None, если пользователь не найден или удалён.
        """
        query = """
        SELECT id, username, email, password
        FROM users
        WHERE id = %s
          AND deleted_at IS NULL
        """
        users = await self.db.fetch(query, user_id)
        return users[0] if users else None

    async def create_user(self, username: str, email: str, password: str) -> dict:
        """
        Создаёт нового пользователя в базе данных.

        Args:
            username (str): Имя пользователя.
            email (str): Email пользователя.
            password (str): Захэшированный пароль.

        Returns:
            dict: Данные созданного пользователя (id, username, email).
        """
        query = """
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
        """
        user_id = await self.db.execute(query, username, email, password)
        return {"id": user_id, "username": username, "email": email}

    async def update_user_in_db(
        self,
        user_id: int,
        username: Optional[str],
        email: Optional[str],
        password: Optional[str]
    ) -> Optional[dict]:
        """
        Обновляет данные активного пользователя в базе.

        Args:
            user_id (int): ID пользователя.
            username (Optional[str]): Новое имя пользователя.
            email (Optional[str]): Новый email.
            password (Optional[str]): Новый пароль.

        Returns:
            Optional[dict]: Обновлённые данные пользователя или None, если пользователь не найден или удалён.
        """
        query = """
        UPDATE users
        SET username = COALESCE(%s, username),
            email = COALESCE(%s, email),
            password = COALESCE(%s, password)
        WHERE id = %s
          AND deleted_at IS NULL
        """
        await self.db.execute(query, username, email, password, user_id)
        return await self.get_user_by_id(user_id)

    async def check_email_exists(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """
        Проверяет, существует ли активный пользователь с указанным email.

        Args:
            email (str): Email пользователя.
            exclude_user_id (Optional[int]): ID пользователя, которого нужно исключить из проверки.

        Returns:
            bool: True, если email уже используется активным пользователем, иначе False.
        """
        query = """
        SELECT id
        FROM users
        WHERE email = %s
          AND deleted_at IS NULL
        """
        if exclude_user_id:
            query += " AND id != %s"
            users = await self.db.fetch(query, email, exclude_user_id)
        else:
            users = await self.db.fetch(query, email)
        return bool(users)

    async def soft_delete_user(self, user_id: int, restoration_token: str) -> bool:
        """
        Помечает пользователя как удалённого и устанавливает токен восстановления.

        Args:
            user_id (int): ID пользователя.
            restoration_token (str): Хэшированный токен восстановления.

        Returns:
            bool: True, если операция успешна, иначе False.
        """
        query = """
        UPDATE users
        SET deleted_at = NOW(), restoration_token = %s
        WHERE id = %s
          AND deleted_at IS NULL
        """
        await self.db.execute(query, restoration_token, user_id)
        return True

    async def restore_user(self, user_id: int) -> bool:
        """
        Восстанавливает удалённого пользователя.

        Args:
            user_id (int): ID пользователя.

        Returns:
            bool: True, если операция успешна, иначе False.
        """
        query = """
        UPDATE users
        SET deleted_at = NULL, restoration_token = NULL
        WHERE id = %s
          AND deleted_at IS NOT NULL
        """
        await self.db.execute(query, user_id)
        return True

    async def get_user_by_restoration_token(self, token: str) -> Optional[dict]:
        """
        Возвращает данные пользователя по токену восстановления.

        Args:
            token (str): Хэшированный токен восстановления.

        Returns:
            Optional[dict]: Данные пользователя или None, если пользователь не найден.
        """
        query = """
        SELECT id, username, email
        FROM users
        WHERE restoration_token = %s
          AND deleted_at IS NOT NULL
        """
        users = await self.db.fetch(query, token)
        return users[0] if users else None