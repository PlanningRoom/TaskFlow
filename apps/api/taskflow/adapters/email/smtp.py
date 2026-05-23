"""SMTP adapter — dev/MailHog path (ADR 067)."""

from __future__ import annotations

import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import aiosmtplib
import structlog

from taskflow.adapters.email.base import EmailMessage
from taskflow.settings import settings

logger = structlog.get_logger(__name__)


class SmtpEmailSender:
    async def send(self, msg: EmailMessage) -> None:
        mime = MIMEMultipart("alternative")
        mime["From"] = formataddr((settings.email_from_name, settings.email_from))
        mime["To"] = msg.to
        mime["Subject"] = msg.subject
        mime.attach(MIMEText(msg.text_body, "plain", "utf-8"))
        mime.attach(MIMEText(msg.html_body, "html", "utf-8"))

        started = time.perf_counter()
        try:
            await aiosmtplib.send(
                mime,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username or None,
                password=settings.smtp_password or None,
                start_tls=False,
            )
        except Exception as exc:
            logger.error(
                "email.send.failure",
                backend="smtp",
                template=msg.template,
                to=msg.to,
                duration_ms=int((time.perf_counter() - started) * 1000),
                exception=type(exc).__name__,
            )
            raise
        logger.info(
            "email.send.success",
            backend="smtp",
            template=msg.template,
            to=msg.to,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
