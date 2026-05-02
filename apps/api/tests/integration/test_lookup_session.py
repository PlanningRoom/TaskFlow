"""Phase B3 — direct rejection-path tests for `lookup_session` (TDD §11.2)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.sessions import create_session, lookup_session
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace
from taskflow.db.uuid7 import uuid7

pytestmark = pytest.mark.asyncio


async def _make_user(db: AsyncSession) -> User:
    workspace = Workspace(name="Aurora")
    db.add(workspace)
    await db.flush()
    user = User(
        workspace_id=workspace.id,
        email=f"u-{uuid7()}@aurora.test",
        name="Aurora User",
        role="owner",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$xxxx$xxxx",  # not verified here
    )
    db.add(user)
    await db.flush()
    return user


async def test_lookup_returns_none_for_unknown_token(db_session: AsyncSession) -> None:
    assert await lookup_session(db_session, "no-such-token-at-all") is None


async def test_lookup_returns_none_for_absolutely_expired_session(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    tokens = await create_session(db_session, user_id=user.id)
    # Force expires_at into the past.
    tokens.session_row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.flush()

    assert await lookup_session(db_session, tokens.session_token) is None


async def test_lookup_returns_none_for_idle_expired_session(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    tokens = await create_session(db_session, user_id=user.id)
    # Push last_seen_at back beyond the 7-day idle window.
    tokens.session_row.last_seen_at = datetime.now(UTC) - timedelta(days=8)
    await db_session.flush()

    assert await lookup_session(db_session, tokens.session_token) is None


async def test_lookup_refreshes_last_seen_on_success(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    tokens = await create_session(db_session, user_id=user.id)

    initial = tokens.session_row.last_seen_at
    # Simulate a small lapse between requests.
    tokens.session_row.last_seen_at = initial - timedelta(minutes=1)
    await db_session.flush()

    refreshed = await lookup_session(db_session, tokens.session_token)
    assert refreshed is not None
    assert refreshed.last_seen_at > initial - timedelta(minutes=1)
