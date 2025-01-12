from app.core.database import Database
from app.api.v1.schemas import UserCreate
from app.api.v1.exceptions import UserAlreadyExistsException, user_already_exists_exception

db = Database()

async def create_user(user: UserCreate):
    query = """
    INSERT INTO users (username, email, password)
    
    """