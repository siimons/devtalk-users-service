from app.core.database import Database


class UserRepository:
    
    def __init__(self, db: Database):
        self.db = db

    async def get_user_by_email(self, email: str) -> dict | None:
        """Получает пользователя по email."""
        query = "SELECT id, username, email, password FROM users WHERE email = %s"
        users = await self.db.fetch(query, email)
        return users[0] if users else None

    async def get_user_by_id(self, user_id: int) -> dict | None:
        """Получает пользователя по ID."""
        query = "SELECT id, username, email FROM users WHERE id = %s"
        users = await self.db.fetch(query, user_id)
        return users[0] if users else None

    async def create_user(self, username: str, email: str, password: str) -> dict:
        """Создаёт нового пользователя."""
        query = """
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
        """
        user_id = await self.db.execute(query, username, email, password)
        return {"id": user_id, "username": username, "email": email}

    async def update_user(
        self, user_id: int, username: str | None, email: str | None, password: str | None
    ) -> dict:
        """Обновляет данные пользователя."""
        query = """
        UPDATE users 
        SET username = COALESCE(%s, username), 
            email = COALESCE(%s, email), 
            password = COALESCE(%s, password)
        WHERE id = %s
        """
        await self.db.execute(query, username, email, password, user_id)
        return {"id": user_id, "username": username, "email": email}

    async def check_email_exists(self, email: str, exclude_user_id: int | None = None) -> bool:
        """Проверяет, существует ли пользователь с таким email."""
        query = "SELECT id FROM users WHERE email = %s"
        if exclude_user_id:
            query += " AND id != %s"
            users = await self.db.fetch(query, email, exclude_user_id)
        else:
            users = await self.db.fetch(query, email)
        return bool(users)