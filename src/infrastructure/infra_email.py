from email.message import EmailMessage

import aiosmtplib

from src.core.config import settings


class SMTPEmailService:
    """Сервис для отправки email через SMTP."""

    async def send_email(self, to_email: str, subject: str, html: str) -> None:
        """Отправка email через SMTP."""
        message = EmailMessage()
        message["From"] = (
            f"{settings.email.sender_name} <{settings.email.sender_email}>"
        )
        message["To"] = to_email
        message["Subject"] = subject

        message.set_content(html, subtype="html")
        message.add_alternative(html, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=settings.email.host,
            port=settings.email.port,
            username=settings.email.username,
            password=settings.email.password,
            start_tls=settings.email.use_tls,
        )
