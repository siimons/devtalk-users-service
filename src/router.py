from fastapi import APIRouter, HTTPException

from src.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    AuthenticationFailedException
)

from src.schemas import (
    UserRegister,
    UserUpdate,
    UserLogin
)

from src.service import (
    add_user,
    verify_password,
    update_user_info
)

router = APIRouter()

@router.post('/api/auth/register/')
async def register_user(user: UserRegister):
    try:
        result = await add_user(user.username, user.email, user.password)
        return result
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=e.message)

@router.post('/api/auth/login/')
async def get_user(user: UserLogin):
    try:
        result = await verify_password(user.email, user.password)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except AuthenticationFailedException as e:
        raise HTTPException(status_code=401, detail=e.message)
    
@router.put('/api/auth/user/{id}')
async def update_user(user: UserUpdate):
    try:
        result = await update_user_info(user.id, user.username, user.email, user.password)
        return result 
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)