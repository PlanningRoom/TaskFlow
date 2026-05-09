"""Activity-event service (ADR 063, PRD §13.2 / §14).

`emit_activity(...)` writes a row inside the caller's transaction. Real-time
fan-out (`publish_event`) is intentionally NOT called here; D1 will add it.

`list_activity(...)` lands in the C5 phase but the helper is colocated for
locality.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.permissions import has_implicit_project_access
from taskflow.db.models.activity_event import ActivityEvent
from taskflow.db.models.project import ProjectMembership
from taskflow.db.models.user import User
from taskflow.errors import NotFoundError
from taskflow.services._pagination import decode_cursor, encode_cursor

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


async def emit_activity(
    db: AsyncSession,
    *,
    event_type: str,
    actor: User,
    workspace_id: UUID,
    project_id: UUID | None,
    subject_type: str,
    subject_id: UUID,
    metadata: dict[str, Any] | None = None,
) -> ActivityEvent:
    row = ActivityEvent(
        workspace_id=workspace_id,
        project_id=project_id,
        actor_id=actor.id,
        event_type=event_type,
        subject_type=subject_type,
        subject_id=subject_id,
        metadata_=metadata or {},
    )
    db.add(row)
    return row


async def list_activity(
    db: AsyncSession,
    *,
    user: User,
    project_id: UUID | None,
    cursor: str | None,
    limit: int = DEFAULT_LIMIT,
) -> tuple[list[ActivityEvent], str | None]:
    """Paginated reverse-chronological feed.

    Workspace scope (project_id None): Member/Viewer rows are filtered by
    `project_memberships`; Owner/Admin see everything.
    Project scope: caller is expected to have already passed
    `assert_project_visible`.
    """
    limit = max(1, min(limit, MAX_LIMIT))
    stmt = select(ActivityEvent).where(ActivityEvent.workspace_id == user.workspace_id)

    if project_id is not None:
        stmt = stmt.where(ActivityEvent.project_id == project_id)
    elif not has_implicit_project_access(user.role):
        # Either the event has no project (workspace-level) OR the caller has
        # an explicit membership row for the event's project.
        stmt = stmt.outerjoin(
            ProjectMembership,
            and_(
                ProjectMembership.project_id == ActivityEvent.project_id,
                ProjectMembership.user_id == user.id,
            ),
        ).where(
            or_(
                ActivityEvent.project_id.is_(None),
                ProjectMembership.user_id == user.id,
            )
        )

    if cursor is not None:
        decoded = decode_cursor(cursor)
        if decoded is not None:
            cur_ts, cur_id = decoded
            stmt = stmt.where(
                or_(
                    ActivityEvent.created_at < cur_ts,
                    and_(
                        ActivityEvent.created_at == cur_ts,
                        ActivityEvent.id < cur_id,
                    ),
                )
            )

    stmt = stmt.order_by(ActivityEvent.created_at.desc(), ActivityEvent.id.desc()).limit(limit + 1)
    rows = list((await db.execute(stmt)).scalars().all())

    next_cursor: str | None = None
    if len(rows) > limit:
        rows = rows[:limit]
        last = rows[-1]
        next_cursor = encode_cursor(last.created_at, last.id)
    return rows, next_cursor


async def get_event(db: AsyncSession, *, event_id: UUID) -> ActivityEvent:
    row = await db.scalar(select(ActivityEvent).where(ActivityEvent.id == event_id))
    if row is None:
        raise NotFoundError("Activity event not found.", code="ACTIVITY_NOT_FOUND")
    return row
