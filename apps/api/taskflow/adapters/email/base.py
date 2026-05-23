"""Email adapter contract (ADR 067).

Two implementations live next door — `smtp.py` (dev / MailHog) and `ses.py`
(prod / Amazon SES). They share the `EmailMessage` payload and `EmailSender`
protocol defined here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class EmailMessage:
    to: str
    subject: str
    text_body: str
    html_body: str
    template: str = "unknown"  # tag used in structured logs, never sent on the wire


@runtime_checkable
class EmailSender(Protocol):
    async def send(self, msg: EmailMessage) -> None: ...
