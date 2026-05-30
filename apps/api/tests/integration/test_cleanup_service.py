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


# ──────────────────────────────────────────────────────────────────────────────
# Backup job: pg_dump + S3 upload paths (ADR 074). pg_dump and aioboto3 are
# mocked — these tests exercise the job's control flow, not real shell-out/S3.
# ──────────────────────────────────────────────────────────────────────────────


class _FakeProc:
    def __init__(self, returncode: int, stdout: bytes = b"", stderr: bytes = b"") -> None:
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    async def communicate(self) -> tuple[bytes, bytes]:
        return self._stdout, self._stderr


class _FakeS3Client:
    def __init__(self, raise_on_put: bool = False) -> None:
        self._raise = raise_on_put
        self.put_calls: list[dict[str, object]] = []

    async def __aenter__(self) -> _FakeS3Client:
        return self

    async def __aexit__(self, *exc: object) -> None:
        return None

    async def put_object(self, **kwargs: object) -> None:
        if self._raise:
            raise RuntimeError("s3 unavailable")
        self.put_calls.append(kwargs)


class _FakeSession:
    def __init__(self, client: _FakeS3Client) -> None:
        self._client = client

    def client(self, *args: object, **kwargs: object) -> _FakeS3Client:
        return self._client


def _patch_pg_dump(monkeypatch: pytest.MonkeyPatch, proc: _FakeProc) -> None:
    async def _fake_exec(*args: object, **kwargs: object) -> _FakeProc:
        return proc

    # String target keeps mypy from type-checking attribute access on the
    # re-exported `asyncio` / `aioboto3` names in the cleanup module.
    monkeypatch.setattr("taskflow.services.cleanup.asyncio.create_subprocess_exec", _fake_exec)


async def test_backup_aborts_when_pg_dump_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    from taskflow.settings import settings

    monkeypatch.setattr(settings, "s3_backups_bucket", "backups-bucket")
    _patch_pg_dump(monkeypatch, _FakeProc(returncode=1, stderr=b"connection refused"))

    s3 = _FakeS3Client()
    monkeypatch.setattr("taskflow.services.cleanup.aioboto3.Session", lambda: _FakeSession(s3))

    # pg_dump failed → returns early, never touches S3.
    await cleanup.backup_database_to_s3()
    assert s3.put_calls == []


async def test_backup_uploads_gzipped_dump_to_s3(monkeypatch: pytest.MonkeyPatch) -> None:
    from taskflow.settings import settings

    monkeypatch.setattr(settings, "s3_backups_bucket", "backups-bucket")
    _patch_pg_dump(monkeypatch, _FakeProc(returncode=0, stdout=b"-- pg_dump output"))

    s3 = _FakeS3Client()
    monkeypatch.setattr("taskflow.services.cleanup.aioboto3.Session", lambda: _FakeSession(s3))

    await cleanup.backup_database_to_s3()

    assert len(s3.put_calls) == 1
    call = s3.put_calls[0]
    assert call["Bucket"] == "backups-bucket"
    assert str(call["Key"]).startswith("backups/")
    assert isinstance(call["Body"], bytes) and call["Body"][:2] == b"\x1f\x8b"  # gzip magic


async def test_backup_swallows_s3_upload_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from taskflow.settings import settings

    monkeypatch.setattr(settings, "s3_backups_bucket", "backups-bucket")
    _patch_pg_dump(monkeypatch, _FakeProc(returncode=0, stdout=b"-- pg_dump output"))

    s3 = _FakeS3Client(raise_on_put=True)
    monkeypatch.setattr("taskflow.services.cleanup.aioboto3.Session", lambda: _FakeSession(s3))

    # Upload raises → caught and logged, no exception propagates.
    await cleanup.backup_database_to_s3()
