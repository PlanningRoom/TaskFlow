"""Resend adapter — prod path (ADR 067, swapped from SES in Phase I2).

Sends transactional email through the Resend HTTP API with `httpx`. The API key
comes from `settings.resend_api_key`, hydrated at boot from the SSM SecureString
`/taskflow/prod/resend_api_key` (ADR 073). Dev/test still use SMTP→MailHog.
"""

from __future__ import annotations

import time

import httpx
import structlog

from taskflow.adapters.email.base import EmailMessage
from taskflow.settings import settings

logger = structlog.get_logger(__name__)

_RESEND_ENDPOINT = "https://api.resend.com/emails"
_TIMEOUT_SECONDS = 10.0


class ResendEmailSender:
    async def send(self, msg: EmailMessage) -> None:
        source = f"{settings.email_from_name} <{settings.email_from}>"
        payload = {
            "from": source,
            "to": [msg.to],
            "subject": msg.subject,
            "text": msg.text_body,
            "html": msg.html_body,
        }
        headers = {"Authorization": f"Bearer {settings.resend_api_key or ''}"}
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
                response = await client.post(_RESEND_ENDPOINT, json=payload, headers=headers)
                response.raise_for_status()
        except Exception as exc:
            logger.error(
                "email.send.failure",
                backend="resend",
                template=msg.template,
                to=msg.to,
                duration_ms=int((time.perf_counter() - started) * 1000),
                exception=type(exc).__name__,
            )
            raise
        logger.info(
            "email.send.success",
            backend="resend",
            template=msg.template,
            to=msg.to,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
