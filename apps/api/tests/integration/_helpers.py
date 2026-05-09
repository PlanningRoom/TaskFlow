"""Shared test helpers for Part C integration tests.

Provides:
  - `signup_owner(http)` — does the canonical owner signup, returns the owner User row.
  - `make_user(db_session, workspace_id, role, email, name)` — inserts a user directly.
  - `auth_client(app, db_session, user)` — creates a session row + AsyncClient with cookies set.
  - `csrf_headers(client)` — extract `X-CSRF-Token` header from a client's cookies.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth import sessions as session_helpers
from taskflow.auth.passwords import hash_password
from taskflow.db.models.user import User
from taskflow.settings import settings

OWNER_PAYLOAD: dict[str, str] = {
    "email": "owner@example.com",
    "password": "correct-horse-battery-staple",
    "display_name": "Aurora Owner",
    "workspace_name": "Aurora Studio",
}


def csrf_headers(client: AsyncClient) -> dict[str, str]:
    csrf = client.cookies.get(settings.csrf_cookie_name)
    assert csrf is not None, "no csrf cookie on client"
    return {settings.csrf_header_name: csrf}


async def signup_owner(http: AsyncClient, payload: dict[str, str] | None = None) -> dict[str, Any]:
    """POST /api/v1/auth/signup with the canonical owner payload (or override).

    Returns the JSON body. The `http` client carries the resulting cookies.
    """
    response = await http.post("/api/v1/auth/signup", json=payload or OWNER_PAYLOAD)
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body


async def make_user(
    db_session: AsyncSession,
    *,
    workspace_id: Any,
    role: str = "member",
    email: str | None = None,
    name: str | None = None,
    password: str = "correct-horse-battery-staple",  # noqa: S107
) -> User:
    """Insert a user directly into a workspace. Returns the persisted row.

    Designed for tests that need a non-Owner caller without going through the
    invitation/accept dance.
    """
    email = email or f"{role}-{name or role}@example.com"
    user = User(
        workspace_id=workspace_id,
        email=email,
        name=name or role.capitalize(),
        role=role,
        password_hash=hash_password(password),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@asynccontextmanager
async def auth_client(
    app: FastAPI,
    db_session: AsyncSession,
    user: User,
) -> AsyncIterator[AsyncClient]:
    """Yield a fresh AsyncClient authenticated as `user` (cookies pre-set)."""
    tokens = await session_helpers.create_session(db_session, user_id=user.id)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        client.cookies.set(settings.session_cookie_name, tokens.session_token)
        client.cookies.set(settings.csrf_cookie_name, tokens.csrf_token)
        yield client
