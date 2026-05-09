"""User-anonymization helper (ADR 065 / TDD §11.7).

Used by both self-account-deletion (`services.auth.delete_account`) and
admin-removes-member (`services.members.remove_user`). Centralizes the
PII-clearing semantics so the two flows can't drift.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth import sessions as session_helpers
from taskflow.db.models.task import Task
from taskflow.db.models.user import User


async def anonymize_user(db: AsyncSession, user: User) -> None:
    """Clear PII in place, drop sessions, unassign tasks. Idempotent.

    - Sets `deleted_at = now()`, NULLs email/name/password_hash.
    - Deletes all sessions for this user.
    - Unassigns the user from any task they were the assignee of.

    Caller is responsible for any further cleanup (e.g. project_memberships)
    and the audit log entry.
    """
    user.email = None
    user.name = None
    user.password_hash = None
    user.deleted_at = datetime.now(UTC)

    await session_helpers.delete_sessions_for_user(db, user.id)
    await db.execute(update(Task).where(Task.assignee_id == user.id).values(assignee_id=None))
