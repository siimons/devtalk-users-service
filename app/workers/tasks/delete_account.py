from celery import shared_task

from app.core.dependencies import get_user_repository
from app.core.logging import logger


@shared_task(
    name="delete_account_permanently",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
)
async def delete_account_permanently(user_id: int) -> None:
    """Окончательно удаляет аккаунт пользователя.

    Args:
        user_id (int): ID пользователя.

    Returns:
        None

    Raises:
        Exception: Если произошла ошибка при удалении аккаунта.
    """
    try:
        user_repo = await get_user_repository()
        await user_repo.hard_delete_user(user_id)
        logger.success(f"Аккаунт {user_id} окончательно удалён.")
    except Exception as e:
        logger.error(f"Ошибка удаления аккаунта {user_id}: {e}")
        raise