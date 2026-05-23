"""Notification dispatch + queries (PRD §15.1, ADR 070).

Each dispatch helper is called from a domain service after the row is
flushed and emits notification rows in the same transaction. Self-trigger
suppression: if `actor.id == recipient.id`, no row is created.
"""

from __future__ import annotations

from datetime import UTC, datetime
from functools import partial
from typing import Any
from uuid import UUID

from fastapi import Request
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.comment import Comment
from taskflow.db.models.notification import Notification
from taskflow.db.models.task import Task
from taskflow.db.models.user import User
from taskflow.errors import NotFoundError
from taskflow.realtime.after_commit import schedule_publish
from taskflow.realtime.publish import publish_to_user
from taskflow.services._pagination import decode_cursor, encode_cursor

DEFAULT_LIMIT = 30
MAX_LIMIT = 100


# ──────────────────────────────────────────────────────────────────────────────
# Dispatch
# ──────────────────────────────────────────────────────────────────────────────


def _row(
    *,
    recipient_id: UUID,
    actor: User,
    event_type: str,
    task: Task,
    metadata: dict[str, Any] | None = None,
) -> Notification:
    return Notification(
        recipient_id=recipient_id,
        actor_id=actor.id,
        event_type=event_type,
        task_id=task.id,
        project_id=task.project_id,
        metadata_=metadata or {},
    )


def _schedule_notification_publish(
    request: Request | None,
    row: Notification,
    workspace_id: UUID,
) -> None:
    if request is None:
        return
    payload = {
        "notification_id": str(row.id),
        "recipient_id": str(row.recipient_id),
        "event_type": row.event_type,
        "task_id": str(row.task_id) if row.task_id else None,
        "project_id": str(row.project_id) if row.project_id else None,
    }
    schedule_publish(
        request,
        partial(
            publish_to_user,
            user_id=row.recipient_id,
            workspace_id=workspace_id,
            event_type="notification.created",
            payload=payload,
        ),
    )


async def dispatch_for_comment(
    db: AsyncSession,
    *,
    actor: User,
    task: Task,
    comment: Comment,
    mentions: list[User],
    request: Request | None = None,
) -> list[Notification]:
    """One row per mentioned user; one for assignee if applicable; de-dup
    so a mentioned-and-assigned recipient gets `mention` only.
    """
    created: list[Notification] = []
    notified_ids: set[UUID] = set()

    for mentioned in mentions:
        if mentioned.id == actor.id:
            continue  # self-suppression
        if mentioned.id in notified_ids:
            continue
        row = _row(
            recipient_id=mentioned.id,
            actor=actor,
            event_type="mention",
            task=task,
            metadata={"comment_id": str(comment.id)},
        )
        db.add(row)
        notified_ids.add(mentioned.id)
        created.append(row)

    if (
        task.assignee_id is not None
        and task.assignee_id != actor.id
        and task.assignee_id not in notified_ids
    ):
        row = _row(
            recipient_id=task.assignee_id,
            actor=actor,
            event_type="task_commented",
            task=task,
            metadata={"comment_id": str(comment.id)},
        )
        db.add(row)
        created.append(row)

    if created:
        await db.flush()  # populate ids for the publish payload
        for row in created:
            _schedule_notification_publish(request, row, task.workspace_id)
    return created


async def dispatch_for_assignment(
    db: AsyncSession,
    *,
    actor: User,
    task: Task,
    new_assignee_id: UUID,
    request: Request | None = None,
) -> Notification | None:
    if new_assignee_id == actor.id:
        return None  # self-suppression
    row = _row(
        recipient_id=new_assignee_id,
        actor=actor,
        event_type="task_assigned",
        task=task,
    )
    db.add(row)
    await db.flush()
    _schedule_notification_publish(request, row, task.workspace_id)
    return row


async def dispatch_for_status_change(
    db: AsyncSession,
    *,
    actor: User,
    task: Task,
    previous_status: str,
    new_status: str,
    request: Request | None = None,
) -> Notification | None:
    if task.assignee_id is None or task.assignee_id == actor.id:
        return None
    row = _row(
        recipient_id=task.assignee_id,
        actor=actor,
        event_type="task_status_changed",
        task=task,
        metadata={"from": previous_status, "to": new_status},
    )
    db.add(row)
    await db.flush()
    _schedule_notification_publish(request, row, task.workspace_id)
    return row


# ──────────────────────────────────────────────────────────────────────────────
# Queries
# ──────────────────────────────────────────────────────────────────────────────


async def list_notifications(
    db: AsyncSession,
    *,
    user: User,
    cursor: str | None,
    limit: int = DEFAULT_LIMIT,
) -> tuple[list[Notification], str | None]:
    limit = max(1, min(limit, MAX_LIMIT))
    stmt = (
        select(Notification)
        .where(Notification.recipient_id == user.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
    )
    if cursor is not None:
        decoded = decode_cursor(cursor)
        if decoded is not None:
            cur_ts, cur_id = decoded
            stmt = stmt.where(
                or_(
                    Notification.created_at < cur_ts,
                    and_(
                        Notification.created_at == cur_ts,
                        Notification.id < cur_id,
                    ),
                )
            )
    rows = list((await db.execute(stmt.limit(limit + 1))).scalars().all())
    next_cursor: str | None = None
    if len(rows) > limit:
        rows = rows[:limit]
        last = rows[-1]
        next_cursor = encode_cursor(last.created_at, last.id)
    return rows, next_cursor


async def unread_count(db: AsyncSession, *, user: User) -> int:
    count = await db.scalar(
        select(func.count(Notification.id)).where(
            Notification.recipient_id == user.id, Notification.read_at.is_(None)
        )
    )
    return int(count or 0)


async def mark_all_read(db: AsyncSession, *, user: User) -> None:
    await db.execute(
        update(Notification)
        .where(Notification.recipient_id == user.id, Notification.read_at.is_(None))
        .values(read_at=datetime.now(UTC))
    )


async def mark_read(db: AsyncSession, *, user: User, notification_id: UUID) -> Notification:
    row = await db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.recipient_id == user.id,
        )
    )
    if row is None:
        raise NotFoundError("Notification not found.", code="NOTIFICATION_NOT_FOUND")
    if row.read_at is None:
        row.read_at = datetime.now(UTC)
    return row
