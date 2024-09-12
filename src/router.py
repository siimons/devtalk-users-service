from fastapi import APIRouter, HTTPException

from src.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    AuthenticationFailedException,
    CommentNotFoundException,
    CommentCreationException,
    CommentDeletionException
)

from src.schemes import (
    UserCreate,
    UserUpdate,
    UserLogin,
    CommentCreate,
    CommentDelete
)

from src.service import (
    add_user,
    verify_password,
    update_user_info,
    add_comment,
    delete_comment
)

router = APIRouter()

@router.post('/api/user/')
async def create_user(user: UserCreate):
    try:
        result = await add_user(user.username, user.email, user.password)
        return result
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=e.message)

@router.post('/api/login/')
async def get_user(user: UserLogin):
    try:
        result = await verify_password(user.email, user.password)
        return result
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except AuthenticationFailedException as e:
        raise HTTPException(status_code=401, detail=e.message)
    
@router.put('/api/user/{id}')
async def update_user(user: UserUpdate):
    try:
        result = await update_user_info(user.id, user.username, user.email, user.password)
        return result 
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    
@router.post('/api/comments/')
async def create_comment(comment: CommentCreate):
    try:
        result = await add_comment(comment.user_id, comment.article_id, comment.content)
        return result
    except CommentCreationException as e:
        raise HTTPException(status_code=500, detail=e.message)
    
@router.delete('/api/comments/')
async def remove_comment(comment: CommentDelete):
    try:
        result = await delete_comment(comment.comment_id, comment.user_id)
        return result
    except CommentNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except CommentDeletionException as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении комментария: {str(e)}")