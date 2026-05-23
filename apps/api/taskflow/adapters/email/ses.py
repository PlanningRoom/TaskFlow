"""SES adapter — prod path (ADR 067).

Credentials resolve via the standard AWS credential chain. In production the
EC2 instance role provides them (ADR 073); locally `AWS_ACCESS_KEY_ID` /
`AWS_SECRET_ACCESS_KEY` env vars work.
"""

from __future__ import annotations

import time

import aioboto3
import structlog

from taskflow.adapters.email.base import EmailMessage
from taskflow.settings import settings

logger = structlog.get_logger(__name__)


class SesEmailSender:
    def __init__(self) -> None:
        self._session = aioboto3.Session()

    async def send(self, msg: EmailMessage) -> None:
        source = f"{settings.email_from_name} <{settings.email_from}>"
        started = time.perf_counter()
        try:
            async with self._session.client("ses", region_name=settings.ses_region) as client:
                await client.send_email(
                    Source=source,
                    Destination={"ToAddresses": [msg.to]},
                    Message={
                        "Subject": {"Data": msg.subject, "Charset": "UTF-8"},
                        "Body": {
                            "Text": {"Data": msg.text_body, "Charset": "UTF-8"},
                            "Html": {"Data": msg.html_body, "Charset": "UTF-8"},
                        },
                    },
                )
        except Exception as exc:
            logger.error(
                "email.send.failure",
                backend="ses",
                template=msg.template,
                to=msg.to,
                duration_ms=int((time.perf_counter() - started) * 1000),
                exception=type(exc).__name__,
            )
            raise
        logger.info(
            "email.send.success",
            backend="ses",
            template=msg.template,
            to=msg.to,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
