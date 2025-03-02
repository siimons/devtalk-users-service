from pydantic import BaseModel, EmailStr, Field


class EmailNotification(BaseModel):
    """
    Схема для отправки email-уведомлений.

    Attributes:
        to_email (EmailStr): Email получателя.
        subject (str): Тема письма.
        template_name (str): Имя шаблона (без расширения .html).
        context (dict): Контекст для шаблона.
    """

    to_email: EmailStr = Field(..., description="Email получателя")
    subject: str = Field(..., description="Тема письма")
    template_name: str = Field(..., description="Имя шаблона (без расширения .html)")
    context: dict = Field(default_factory=dict, description="Контекст для шаблона")


class RestorationEmailNotification(EmailNotification):
    """
    Схема для отправки email с токеном восстановления.

    Attributes:
        restoration_token (str): Токен восстановления аккаунта.
    """

    restoration_token: str = Field(..., description="Токен восстановления аккаунта")

    def __init__(self, **data):
        super().__init__(
            subject="Account Restoration",
            template_name="restoration_token",
            context={"restoration_token": data["restoration_token"]},
            **data,
        )
