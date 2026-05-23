"""Phase D2 — cleanup service against a real database."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.passwords import hash_password
from taskflow.auth.tokens import generate_token
from taskflow.db.models.invitation import Invitation
from taskflow.db.models.password_reset_token import PasswordResetToken
from taskflow.db.models.session import Session
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace
from taskflow.services import cleanup

pytestmark = pytest.mark.asyncio


async def _seed_workspace_and_user(db_session: AsyncSession) -> User:
    workspace = Workspace(name="Cleanup WS")
    db_session.add(workspace)
    await db_session.flush()
    user = User(
        workspace_id=workspace.id,
        email="owner@example.com",
        name="Owner",
        role="owner",
        password_hash=hash_password("hunter2hunter2"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def test_expire_invitations_removes_only_expired(db_session: AsyncSession) -> None:
    user = await _seed_workspace_and_user(db_session)
    now = datetime.now(UTC)

    expired_raw, expired_hash = generate_token(16)
    fresh_raw, fresh_hash = generate_token(16)
    accepted_raw, accepted_hash = generate_token(16)
    _ = (expired_raw, fresh_raw, accepted_raw)

    db_session.add(
        Invitation(
            workspace_id=user.workspace_id,
            email="expired@example.com",
            role="member",
            token_hash=expired_hash,
            invited_by=user.id,
            expires_at=now - timedelta(days=1),
        )
    )
    db_session.add(
        Invitation(
            workspace_id=user.workspace_id,
            email="fresh@example.com",
            role="member",
            token_hash=fresh_hash,
            invited_by=user.id,
            expires_at=now + timedelta(days=1),
        )
    )
    db_session.add(
        Invitation(
            workspace_id=user.workspace_id,
            email="accepted@example.com",
            role="member",
            token_hash=accepted_hash,
            invited_by=user.id,
            expires_at=now - timedelta(days=1),
            accepted_at=now - timedelta(hours=2),
        )
    )
    await db_session.commit()

    count = await cleanup.expire_invitations()
    assert count == 1

    rows = (await db_session.execute(select(Invitation.email))).scalars().all()
    assert set(rows) == {"fresh@example.com", "accepted@example.com"}


async def test_delete_expired_sessions(db_session: AsyncSession) -> None:
    user = await _seed_workspace_and_user(db_session)
    now = datetime.now(UTC)

    db_session.add(
        Session(
            id=b"\x01" * 32,
            user_id=user.id,
            csrf_token=b"\x02" * 32,
            expires_at=now - timedelta(hours=1),
            last_seen_at=now - timedelta(hours=2),
        )
    )
    db_session.add(
        Session(
            id=b"\x03" * 32,
            user_id=user.id,
            csrf_token=b"\x04" * 32,
            expires_at=now + timedelta(days=7),
            last_seen_at=now,
        )
    )
    await db_session.commit()

    count = await cleanup.delete_expired_sessions()
    assert count == 1

    remaining = (await db_session.execute(select(Session))).scalars().all()
    assert len(remaining) == 1
    assert remaining[0].id == b"\x03" * 32


async def test_delete_expired_password_reset_tokens(db_session: AsyncSession) -> None:
    user = await _seed_workspace_and_user(db_session)
    now = datetime.now(UTC)

    db_session.add(
        PasswordResetToken(
            token_hash=b"\x10" * 32,
            user_id=user.id,
            expires_at=now - timedelta(minutes=5),
        )
    )
    db_session.add(
        PasswordResetToken(
            token_hash=b"\x11" * 32,
            user_id=user.id,
            expires_at=now + timedelta(hours=1),
            used_at=now - timedelta(minutes=1),
        )
    )
    db_session.add(
        PasswordResetToken(
            token_hash=b"\x12" * 32,
            user_id=user.id,
            expires_at=now + timedelta(hours=1),
        )
    )
    await db_session.commit()

    count = await cleanup.delete_expired_password_reset_tokens()
    assert count == 2

    remaining = (await db_session.execute(select(PasswordResetToken))).scalars().all()
    assert len(remaining) == 1
    assert remaining[0].token_hash == b"\x12" * 32


async def test_backup_skipped_when_bucket_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    from taskflow.settings import settings

    monkeypatch.setattr(settings, "s3_backups_bucket", None)
    # No exception, no error.
    await cleanup.backup_database_to_s3()
