from app.core.database import Database


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

    async def get_user_by_email(self, email: str) -> dict | None:
        """
        Возвращает данные пользователя по email.

        Args:
            email (str): Email пользователя.

        Returns:
            dict | None: Данные пользователя или None, если пользователь не найден.
        """
        query = "SELECT id, username, email, password FROM users WHERE email = %s"
        users = await self.db.fetch(query, email)
        return users[0] if users else None

    async def get_user_by_id(self, user_id: int) -> dict | None:
        """
        Возвращает данные пользователя по ID.

        Args:
            user_id (int): Уникальный идентификатор пользователя.

        Returns:
            dict | None: Данные пользователя или None, если пользователь не найден.
        """
        query = "SELECT id, username, email, password FROM users WHERE id = %s"
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
        self, user_id: int, username: str | None, email: str | None, password: str | None
    ) -> dict | None:
        """
        Обновляет данные пользователя в базе.

        Args:
            user_id (int): ID пользователя.
            username (str | None, optional): Новое имя пользователя (если передано).
            email (str | None, optional): Новый email (если передан).
            password (str | None, optional): Новый пароль (если передан).

        Returns:
            dict | None: Обновлённые данные пользователя или None, если пользователь не найден.
        """
        query = """
        UPDATE users
        SET username = COALESCE(%s, username),
            email = COALESCE(%s, email),
            password = COALESCE(%s, password)
        WHERE id = %s
        """
        await self.db.execute(query, username, email, password, user_id)
        updated_user = await self.get_user_by_id(user_id)
        return updated_user

    async def check_email_exists(self, email: str, exclude_user_id: int | None = None) -> bool:
        """
        Проверяет, существует ли пользователь с указанным email.

        Args:
            email (str): Email пользователя.
            exclude_user_id (int | None, optional): ID пользователя, которого нужно исключить из проверки.

        Returns:
            bool: True, если email уже используется, иначе False.
        """
        query = "SELECT id FROM users WHERE email = %s"
        if exclude_user_id:
            query += " AND id != %s"
            users = await self.db.fetch(query, email, exclude_user_id)
        else:
            users = await self.db.fetch(query, email)
        return bool(users)
    