"""Periodic cleanup + backup jobs invoked by the APScheduler (ADR 069, 074).

Each function opens its own session via `session_scope()` because the
scheduler runs outside any request lifecycle.
"""

from __future__ import annotations

import asyncio
import gzip
import time
from datetime import UTC, datetime
from typing import Any, cast

import aioboto3
import structlog
from sqlalchemy import CursorResult, delete, or_

from taskflow.db.models.invitation import Invitation
from taskflow.db.models.password_reset_token import PasswordResetToken
from taskflow.db.models.session import Session
from taskflow.db.session import session_scope
from taskflow.settings import settings

logger = structlog.get_logger(__name__)


async def expire_invitations() -> int:
    """Delete pending invitations whose `expires_at` has passed."""
    now = datetime.now(UTC)
    async with session_scope() as db:
        result = await db.execute(
            delete(Invitation).where(
                Invitation.expires_at <= now,
                Invitation.accepted_at.is_(None),
            )
        )
        await db.commit()
    count = cast("CursorResult[Any]", result).rowcount or 0
    logger.info("cleanup.invitations.purged", count=count)
    return count


async def delete_expired_sessions() -> int:
    """Delete session rows whose `expires_at` has passed."""
    now = datetime.now(UTC)
    async with session_scope() as db:
        result = await db.execute(delete(Session).where(Session.expires_at <= now))
        await db.commit()
    count = cast("CursorResult[Any]", result).rowcount or 0
    logger.info("cleanup.sessions.purged", count=count)
    return count


async def delete_expired_password_reset_tokens() -> int:
    """Delete password-reset tokens that are expired or already consumed."""
    now = datetime.now(UTC)
    async with session_scope() as db:
        result = await db.execute(
            delete(PasswordResetToken).where(
                or_(
                    PasswordResetToken.expires_at <= now,
                    PasswordResetToken.used_at.is_not(None),
                )
            )
        )
        await db.commit()
    count = cast("CursorResult[Any]", result).rowcount or 0
    logger.info("cleanup.password_reset_tokens.purged", count=count)
    return count


async def backup_database_to_s3() -> None:
    """Snapshot the database with `pg_dump` and stream it to S3 (ADR 074).

    No-op when `S3_BACKUPS_BUCKET` is unset (dev posture). The DB URL is
    translated from the SQLAlchemy `asyncpg` form to a libpq-compatible URL
    before being handed to `pg_dump`.
    """
    bucket = settings.s3_backups_bucket
    if not bucket:
        logger.info("backup.skipped", reason="bucket_unset")
        return

    libpq_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    now = datetime.now(UTC)
    key = f"backups/{now:%Y}/{now:%m}/{now:%d}/taskflow-{now:%Y%m%dT%H%M%SZ}.sql.gz"

    started = time.perf_counter()
    try:
        proc = await asyncio.create_subprocess_exec(
            "pg_dump",
            "--no-owner",
            "--no-privileges",
            libpq_url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error(
                "backup.failure",
                stage="pg_dump",
                returncode=proc.returncode,
                stderr=stderr.decode("utf-8", errors="replace")[:500],
            )
            return

        body = gzip.compress(stdout)
        session = aioboto3.Session()
        async with session.client("s3", region_name=settings.aws_region) as s3:
            await s3.put_object(Bucket=bucket, Key=key, Body=body)
    except Exception as exc:
        logger.error(
            "backup.failure",
            stage="upload",
            exception=type(exc).__name__,
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        return

    logger.info(
        "backup.success",
        bucket=bucket,
        key=key,
        bytes=len(body),
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
