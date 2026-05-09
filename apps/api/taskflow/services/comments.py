"""Comment service (PRD §11, ADR 088 — author-only edit/delete)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import Request
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.comment import Comment
from taskflow.db.models.task import Task
from taskflow.db.models.user import User
from taskflow.errors import NotFoundError, PermissionDeniedError
from taskflow.services.activity import emit_activity
from taskflow.services.mentions import resolve_mentions
from taskflow.services.tasks import assert_task_accessible


async def list_task_comments(
    db: AsyncSession, *, user: User, task_id: UUID
) -> tuple[list[Comment], dict[UUID, list[User]]]:
    """Return (comments oldest-first, {comment_id: [mentioned_users]})."""
    await assert_task_accessible(db, user=user, task_id=task_id)
    rows = await db.execute(
        select(Comment)
        .where(Comment.task_id == task_id)
        .order_by(asc(Comment.created_at), asc(Comment.id))
    )
    comments = list(rows.scalars().all())
    mentions_by_id: dict[UUID, list[User]] = {}
    for c in comments:
        mentions_by_id[c.id] = await resolve_mentions(
            db, body=c.body, workspace_id=user.workspace_id
        )
    return comments, mentions_by_id


async def create_comment(
    db: AsyncSession,
    *,
    actor: User,
    task_id: UUID,
    body: str,
    request: Request | None = None,
) -> tuple[Comment, list[User], Task]:
    task = await assert_task_accessible(db, user=actor, task_id=task_id)
    comment = Comment(task_id=task_id, author_id=actor.id, body=body)
    db.add(comment)
    await db.flush()

    mentions = await resolve_mentions(db, body=body, workspace_id=actor.workspace_id)

    await emit_activity(
        db,
        event_type="comment.created",
        actor=actor,
        workspace_id=actor.workspace_id,
        project_id=task.project_id,
        subject_type="comment",
        subject_id=comment.id,
        metadata={
            "task_id": str(task_id),
            "preview": body[:120],
        },
    )

    from taskflow.services.notifications import dispatch_for_comment

    await dispatch_for_comment(db, actor=actor, task=task, comment=comment, mentions=mentions)
    return comment, mentions, task


async def _load_comment_or_404(
    db: AsyncSession, *, workspace_id: UUID, comment_id: UUID
) -> tuple[Comment, Task]:
    """Load comment + parent task; 404 on miss or cross-workspace."""
    row = await db.execute(
        select(Comment, Task)
        .join(Task, Task.id == Comment.task_id)
        .where(Comment.id == comment_id, Task.workspace_id == workspace_id)
    )
    pair = row.first()
    if pair is None:
        raise NotFoundError("Comment not found.", code="COMMENT_NOT_FOUND")
    return pair[0], pair[1]


def _ensure_author(comment: Comment, actor: User) -> None:
    """ADR 088: only the author can edit/delete their own comment."""
    if comment.author_id != actor.id:
        raise PermissionDeniedError(
            "You can only modify your own comments.", code="PERMISSION_DENIED"
        )


async def update_comment(
    db: AsyncSession,
    *,
    actor: User,
    comment_id: UUID,
    body: str,
    request: Request | None = None,
) -> tuple[Comment, list[User], Task]:
    comment, task = await _load_comment_or_404(
        db, workspace_id=actor.workspace_id, comment_id=comment_id
    )
    _ensure_author(comment, actor)
    comment.body = body
    comment.updated_at = datetime.now(UTC)
    mentions = await resolve_mentions(db, body=body, workspace_id=actor.workspace_id)
    return comment, mentions, task


async def delete_comment(
    db: AsyncSession,
    *,
    actor: User,
    comment_id: UUID,
    request: Request | None = None,
) -> None:
    comment, _task = await _load_comment_or_404(
        db, workspace_id=actor.workspace_id, comment_id=comment_id
    )
    _ensure_author(comment, actor)
    await db.delete(comment)
