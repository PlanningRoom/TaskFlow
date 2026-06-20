"""SMTP and Resend adapter unit tests (Phase D2; SES → Resend swap in I2)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from taskflow.adapters.email.base import EmailMessage
from taskflow.adapters.email.resend import ResendEmailSender
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
async def test_resend_sender_invokes_httpx(monkeypatch: pytest.MonkeyPatch) -> None:
    from taskflow.settings import settings

    monkeypatch.setattr(settings, "resend_api_key", "re_test_key", raising=False)

    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

    fake_post = AsyncMock(return_value=_FakeResponse())

    class _FakeClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.post = fake_post

        async def __aenter__(self) -> _FakeClient:
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

    monkeypatch.setattr("taskflow.adapters.email.resend.httpx.AsyncClient", _FakeClient)

    sender = ResendEmailSender()
    await sender.send(
        EmailMessage(
            to="recipient@example.com",
            subject="Hello",
            text_body="text body",
            html_body="<p>html body</p>",
            template="invitation",
        )
    )

    fake_post.assert_awaited_once()
    call = fake_post.await_args
    assert call is not None
    args, kwargs = call.args, call.kwargs
    assert args[0] == "https://api.resend.com/emails"
    assert kwargs["headers"]["Authorization"] == "Bearer re_test_key"
    body = kwargs["json"]
    assert body["to"] == ["recipient@example.com"]
    assert body["subject"] == "Hello"
    assert body["text"] == "text body"
    assert body["html"] == "<p>html body</p>"
    assert body["from"] == "TaskFlow <no-reply@taskflow.local>"
