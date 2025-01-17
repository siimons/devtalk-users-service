from app.core.database import Database

db = Database()

async def get_database() -> Database:
    """
    Dependency для получения объекта Database.
    """
    if not db.pool:
        await db.connect()
    return db