from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pymysql import MySQLError

from src.schemes import (
    UserCreate,
    UserResponse,
    UserUpdate,
)

from src.service import (
    add_user,
)

router = APIRouter()

@router.post('/api/users/')
async def create_user(user: UserCreate):
    
    result = await add_user(user.username, user.email, user.password)
    
    return result