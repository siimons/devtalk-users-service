from celery import shared_task

from app.notifications.email import EmailSender
from app.notifications.schemas import RestorationEmailNotification

from app.core.logging import logger


@shared_task(
    name="send_restoration_email",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    time_limit=30,
)
def send_restoration_email(to_email: str, restoration_token: str) -> bool:
    """
    Задача Celery для отправки email с токеном восстановления.

    Args:
        to_email (str): Email получателя.
        restoration_token (str): Токен восстановления аккаунта.

    Returns:
        bool: True, если письмо отправлено успешно, иначе False.
    """
    try:
        email_sender = EmailSender()
        notification = RestorationEmailNotification(
            to_email=to_email,
            restoration_token=restoration_token,
        )

        success = email_sender.send_email(
            to_email=notification.to_email,
            subject=notification.subject,
            template_name=notification.template_name,
            context=notification.context,
        )

        if success:
            logger.success(f"Письмо с токеном восстановления отправлено на {to_email}")
        else:
            logger.error(f"Не удалось отправить письмо с токеном восстановления на {to_email}")

        return success

    except Exception as e:
        logger.error(f"Ошибка при отправке письма с токеном восстановления на {to_email}: {str(e)}")
        raise