from pathlib import Path
from typing import Optional, Dict

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader
from premailer import transform

from app.core.settings import settings
from app.core.logging import logger


class EmailSender:
    """Класс для отправки электронных писем через SMTP."""

    def __init__(self):
        """Инициализирует SMTP-клиент и загрузчик шаблонов."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME

        self.template_env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"),
            autoescape=True,
        )

    def _render_template(self, template_name: str, context: Dict) -> str:
        """Рендерит HTML-шаблон с использованием переданного контекста.

        Args:
            template_name (str): Имя шаблона (без расширения .html).
            context (Dict): Словарь с данными для шаблона.

        Returns:
            str: Рендеренный HTML-код.

        Raises:
            Exception: Если шаблон не найден или произошла ошибка при рендеринге.
        """
        try:
            template = self.template_env.get_template(f"{template_name}.html")
            return template.render(context)
        except Exception as e:
            logger.error(f"Ошибка при рендеринге шаблона {template_name}: {str(e)}")
            raise

    def _inline_styles(self, html_content: str) -> str:
        """Преобразует CSS в inline-стили.

        Args:
            html_content (str): HTML-код с тегами <style>.

        Returns:
            str: HTML-код с inline-стилями.
        """
        try:
            return transform(html_content)
        except Exception as e:
            logger.error(f"Ошибка при преобразовании стилей: {str(e)}")
            return html_content

    def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Optional[Dict] = None,
        text_content: Optional[str] = None,
    ) -> bool:
        """Отправляет электронное письмо.

        Args:
            to_email (str): Email получателя.
            subject (str): Тема письма.
            template_name (str): Имя шаблона (без расширения .html).
            context (Optional[Dict]): Контекст для шаблона. По умолчанию None.
            text_content (Optional[str]): Текстовая версия письма. По умолчанию None.

        Returns:
            bool: True, если письмо отправлено успешно, иначе False.
        """
        if context is None:
            context = {}

        try:
            html_content = self._render_template(template_name, context)
            html_content = self._inline_styles(html_content)

            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            if text_content:
                msg.attach(MIMEText(text_content, "plain"))

            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Письмо успешно отправлено на {to_email}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при отправке письма на {to_email}: {str(e)}")
            return False