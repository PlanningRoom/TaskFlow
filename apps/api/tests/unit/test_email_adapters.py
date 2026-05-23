"""Phase D2 — SMTP and SES adapter unit tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from taskflow.adapters.email.base import EmailMessage
from taskflow.adapters.email.ses import SesEmailSender
from taskflow.adapters.email.smtp import SmtpEmailSender


@pytest.mark.asyncio
async def test_smtp_sender_invokes_aiosmtplib(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: dict[str, Any] = {}

    async def fake_send(mime: Any, **kwargs: Any) -> None:
        sent["mime"] = mime
        sent["kwargs"] = kwargs

    monkeypatch.setattr("taskflow.adapters.email.smtp.aiosmtplib.send", fake_send)

    sender = SmtpEmailSender()
    await sender.send(
        EmailMessage(
            to="recipient@example.com",
            subject="Hello",
            text_body="text body",
            html_body="<p>html body</p>",
            template="invitation",
        )
    )

    mime = sent["mime"]
    assert mime["To"] == "recipient@example.com"
    assert mime["Subject"] == "Hello"
    # multipart/alternative carries both text and html
    parts = mime.get_payload()
    assert len(parts) == 2
    assert parts[0].get_content_type() == "text/plain"
    assert parts[1].get_content_type() == "text/html"
    assert sent["kwargs"]["hostname"] == "mailhog"
    assert sent["kwargs"]["port"] == 1025


@pytest.mark.asyncio
async def test_ses_sender_invokes_send_email(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = MagicMock()
    fake_client.send_email = AsyncMock()

    class _ClientCtx:
        async def __aenter__(self) -> MagicMock:
            return fake_client

        async def __aexit__(self, *args: Any) -> None:
            return None

    class _FakeSession:
        def client(self, *args: Any, **kwargs: Any) -> _ClientCtx:
            return _ClientCtx()

    monkeypatch.setattr(
        "taskflow.adapters.email.ses.aioboto3.Session",
        lambda: _FakeSession(),
    )

    sender = SesEmailSender()
    await sender.send(
        EmailMessage(
            to="recipient@example.com",
            subject="Hello",
            text_body="text body",
            html_body="<p>html body</p>",
            template="invitation",
        )
    )

    fake_client.send_email.assert_awaited_once()
    kwargs = fake_client.send_email.await_args.kwargs
    assert kwargs["Destination"] == {"ToAddresses": ["recipient@example.com"]}
    assert kwargs["Message"]["Subject"]["Data"] == "Hello"
    assert kwargs["Message"]["Body"]["Text"]["Data"] == "text body"
    assert kwargs["Message"]["Body"]["Html"]["Data"] == "<p>html body</p>"
