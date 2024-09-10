from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pymysql import MySQLError

from src.schemes import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserLogin
)

from src.service import (
    add_user,
    verify_password
)

router = APIRouter()

@router.post('/api/users/')
async def create_user(user: UserCreate):
    
    result = await add_user(user.username, user.email, user.password)
    
    return result

@router.post('/api/login/')
async def get_user_by_email(user: UserLogin):

    result = await verify_password(user.email, user.password)

    return result