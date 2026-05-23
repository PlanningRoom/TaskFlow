"""Phase D2 — invitation + password-reset endpoints dispatch real emails."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from taskflow.settings import settings
from tests.conftest import FakeEmailSender
from tests.integration._helpers import csrf_headers, signup_owner

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def app(db_engine: None) -> FastAPI:
    settings.cookie_secure = False
    from taskflow.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
async def http(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


async def test_send_invitation_dispatches_email(
    http: AsyncClient, email_sender: FakeEmailSender
) -> None:
    await signup_owner(http)
    response = await http.post(
        "/api/v1/workspaces/me/invitations",
        json={"email": "newhire@example.com", "role": "member"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text

    assert len(email_sender.sent) == 1
    msg = email_sender.sent[0]
    assert msg.to == "newhire@example.com"
    assert msg.template == "invitation"
    assert "Aurora Studio" in msg.subject
    assert settings.frontend_base_url.rstrip("/") + "/invitations/" in msg.text_body


async def test_password_reset_request_dispatches_email(
    http: AsyncClient, email_sender: FakeEmailSender
) -> None:
    await signup_owner(http)

    response = await http.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "owner@example.com"},
    )
    assert response.status_code == 200, response.text

    assert len(email_sender.sent) == 1
    msg = email_sender.sent[0]
    assert msg.to == "owner@example.com"
    assert msg.template == "password_reset"
    assert "/reset-password?token=" in msg.text_body


async def test_password_reset_request_unknown_email_no_email_sent(
    http: AsyncClient, email_sender: FakeEmailSender
) -> None:
    response = await http.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "ghost@example.com"},
    )
    # No-enumeration: still returns 200, but no email is dispatched.
    assert response.status_code == 200
    assert email_sender.sent == []
