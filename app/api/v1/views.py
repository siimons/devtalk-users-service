from fastapi import APIRouter, HTTPException, status

from app.core.database import Database

from app.api.v1.schemas import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserDelete,
    User
)

from app.api.v1.exceptions import (
    InvalidCredentialsException,
    invalid_credentials_exception
)

router = APIRouter()

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate):
    pass