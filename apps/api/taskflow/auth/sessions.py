"""Server-side session creation, lookup, cleanup (ADR 047, TDD §11.2).

CSRF token: 32 raw bytes are stored in `sessions.csrf_token` (TDD §8.2). The
URL-safe base64 form is what travels in the cookie + `X-CSRF-Token` header
(43 ASCII chars). `auth.csrf.csrf_check` does the base64 → bytes decode and
compares constant-time against the stored bytes.
"""

from __future__ import annotations

import base64
import binascii
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.tokens import generate_token, hash_token
from taskflow.db.models.session import Session as SessionModel
from taskflow.settings import settings

CSRF_BYTES = 32


def encode_csrf(raw: bytes) -> str:
    """URL-safe base64-encode the raw CSRF bytes for cookie transport."""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def decode_csrf(encoded: str) -> bytes | None:
    """Inverse of `encode_csrf`. Returns None on malformed input."""
    try:
        padded = encoded + "=" * (-len(encoded) % 4)
        return base64.urlsafe_b64decode(padded.encode("ascii"))
    except (ValueError, binascii.Error):
        return None


class SessionTokens:
    """Plaintext session + CSRF tokens to set as cookies on the response."""

    __slots__ = ("session_token", "csrf_token", "session_row")

    def __init__(self, session_token: str, csrf_token: str, session_row: SessionModel) -> None:
        self.session_token = session_token
        self.csrf_token = csrf_token
        self.session_row = session_row


async def create_session(
    db: AsyncSession,
    *,
    user_id: UUID,
    ip: str | None = None,
    user_agent: str | None = None,
    now: datetime | None = None,
) -> SessionTokens:
    """Create a new session row and return the plaintext tokens for cookies."""
    now = now or datetime.now(UTC)
    session_token, session_id_hash = generate_token(32)
    csrf_raw_bytes = secrets.token_bytes(CSRF_BYTES)

    row = SessionModel(
        id=session_id_hash,
        user_id=user_id,
        csrf_token=csrf_raw_bytes,
        expires_at=now + timedelta(days=settings.session_absolute_ttl_days),
        last_seen_at=now,
        ip=ip,
        user_agent=user_agent,
    )
    db.add(row)
    await db.flush()
    return SessionTokens(
        session_token=session_token,
        csrf_token=encode_csrf(csrf_raw_bytes),
        session_row=row,
    )


async def lookup_session(
    db: AsyncSession,
    raw_session_token: str,
    *,
    now: datetime | None = None,
) -> SessionModel | None:
    """Validate and refresh a session by raw cookie value.

    Returns None on:
      - missing row
      - absolute expiry (`expires_at < now`)
      - idle expiry (`last_seen_at < now - idle_ttl`)

    Updates `last_seen_at = now` on success (in-place; caller must commit).
    """
    now = now or datetime.now(UTC)
    session_id_hash = hash_token(raw_session_token)
    row = await db.scalar(select(SessionModel).where(SessionModel.id == session_id_hash))
    if row is None:
        return None

    if row.expires_at <= now:
        return None

    idle_cutoff = now - timedelta(days=settings.session_idle_ttl_days)
    if row.last_seen_at < idle_cutoff:
        return None

    row.last_seen_at = now
    return row


async def delete_session(db: AsyncSession, raw_session_token: str) -> None:
    """Delete a single session by raw cookie value (logout)."""
    await db.execute(delete(SessionModel).where(SessionModel.id == hash_token(raw_session_token)))


async def delete_sessions_for_user(
    db: AsyncSession,
    user_id: UUID,
    *,
    except_session_id: bytes | None = None,
) -> None:
    """Revoke all sessions for a user (logout-all, password change/reset, removal)."""
    stmt = delete(SessionModel).where(SessionModel.user_id == user_id)
    if except_session_id is not None:
        stmt = stmt.where(SessionModel.id != except_session_id)
    await db.execute(stmt)


async def cleanup_expired_sessions(db: AsyncSession, *, now: datetime | None = None) -> int:
    """Remove sessions past their absolute expiry. Returns the row count."""
    now = now or datetime.now(UTC)
    result = await db.execute(delete(SessionModel).where(SessionModel.expires_at <= now))
    rowcount: int = getattr(result, "rowcount", 0) or 0
    return rowcount
