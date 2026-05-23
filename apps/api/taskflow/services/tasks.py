"""Task service (PRD §6, ADR 008/040/062)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from functools import partial
from typing import Any, cast
from uuid import UUID

from fastapi import Request
from sqlalchemy import and_, case, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.permissions import has_implicit_project_access
from taskflow.db.models.label import Label, TaskLabel
from taskflow.db.models.project import ProjectMembership
from taskflow.db.models.task import Task
from taskflow.db.models.user import User
from taskflow.errors import AppError, NotFoundError
from taskflow.services._pagination import decode_cursor, encode_cursor
from taskflow.services.activity import emit_activity
from taskflow.services.projects import assert_project_visible

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


class InvalidAssigneeError(AppError):
    code = "INVALID_ASSIGNEE"
    status_code = 422


class InvalidLabelError(AppError):
    code = "INVALID_LABEL"
    status_code = 422


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


async def _load_task_or_404(db: AsyncSession, *, workspace_id: UUID, task_id: UUID) -> Task:
    task = await db.scalar(
        select(Task).where(Task.id == task_id, Task.workspace_id == workspace_id)
    )
    if task is None:
        raise NotFoundError("Task not found.", code="TASK_NOT_FOUND")
    return task


async def assert_task_accessible(db: AsyncSession, *, user: User, task_id: UUID) -> Task:
    """Used by routes that take `/tasks/:task_id` (no project_id in path)."""
    task = await _load_task_or_404(db, workspace_id=user.workspace_id, task_id=task_id)
    await assert_project_visible(db, user=user, project_id=task.project_id)
    return task


async def _validate_assignee(
    db: AsyncSession,
    *,
    workspace_id: UUID,
    project_id: UUID,
    assignee_id: UUID,
) -> None:
    user = await db.scalar(
        select(User).where(
            User.id == assignee_id,
            User.workspace_id == workspace_id,
            User.deleted_at.is_(None),
        )
    )
    if user is None:
        raise InvalidAssigneeError("Assignee is not a workspace member.")
    # Owner/Admin have implicit project access.
    if has_implicit_project_access(user.role):
        return
    membership = await db.scalar(
        select(ProjectMembership).where(
            ProjectMembership.project_id == project_id,
            ProjectMembership.user_id == user.id,
        )
    )
    if membership is None:
        raise InvalidAssigneeError("Assignee does not have access to this project.")


async def _validate_label_ids(
    db: AsyncSession, *, workspace_id: UUID, label_ids: list[UUID]
) -> None:
    if not label_ids:
        return
    rows = await db.execute(
        select(Label.id).where(Label.workspace_id == workspace_id, Label.id.in_(label_ids))
    )
    found = set(rows.scalars().all())
    missing = set(label_ids) - found
    if missing:
        raise InvalidLabelError("One or more labels do not belong to this workspace.")


# ──────────────────────────────────────────────────────────────────────────────
# Filters / list
# ──────────────────────────────────────────────────────────────────────────────


_PRIORITY_RANK = {
    "urgent": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
    "none": 5,
}


def _due_filter_clause(due: str) -> Any:
    today = date.today()
    if due == "overdue":
        return and_(
            Task.due_date.is_not(None),
            Task.due_date < today,
            Task.status.notin_(("done", "cancelled")),
        )
    if due == "today":
        return Task.due_date == today
    if due == "this_week":
        end = today + timedelta(days=6)
        return and_(Task.due_date >= today, Task.due_date <= end)
    if due == "no_due_date":
        return Task.due_date.is_(None)
    return None


async def list_tasks(
    db: AsyncSession,
    *,
    project_id: UUID,
    workspace_id: UUID,
    status: list[str] | None = None,
    assignees: list[UUID] | None = None,
    priorities: list[str] | None = None,
    label_ids: list[UUID] | None = None,
    due: str | None = None,
    include_cancelled: bool = False,
    sort: str = "created_at",
    cursor: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> tuple[list[Task], str | None]:
    limit = max(1, min(limit, MAX_LIMIT))

    stmt = select(Task).where(Task.project_id == project_id, Task.workspace_id == workspace_id)

    if status:
        stmt = stmt.where(Task.status.in_(status))
    elif not include_cancelled:
        stmt = stmt.where(Task.status != "cancelled")

    if assignees:
        stmt = stmt.where(Task.assignee_id.in_(assignees))
    if priorities:
        stmt = stmt.where(Task.priority.in_(priorities))
    if label_ids:
        stmt = stmt.join(TaskLabel, TaskLabel.task_id == Task.id).where(
            TaskLabel.label_id.in_(label_ids)
        )
    if due:
        clause = _due_filter_clause(due)
        if clause is not None:
            stmt = stmt.where(clause)

    if sort == "priority":
        rank = case(_PRIORITY_RANK, value=Task.priority, else_=99)
        stmt = stmt.order_by(rank.asc(), Task.created_at.desc(), Task.id.desc())
    elif sort == "due_date":
        stmt = stmt.order_by(
            Task.due_date.is_(None).asc(),
            Task.due_date.asc(),
            Task.created_at.desc(),
            Task.id.desc(),
        )
    elif sort == "assignee":
        stmt = stmt.outerjoin(User, User.id == Task.assignee_id).order_by(
            User.name.asc().nulls_last(),
            Task.created_at.desc(),
            Task.id.desc(),
        )
    else:  # created_at (default — descending newest-first)
        stmt = stmt.order_by(Task.created_at.desc(), Task.id.desc())

    if cursor is not None and sort == "created_at":
        decoded = decode_cursor(cursor)
        if decoded is not None:
            cur_ts, cur_id = decoded
            stmt = stmt.where(
                or_(
                    Task.created_at < cur_ts,
                    and_(Task.created_at == cur_ts, Task.id < cur_id),
                )
            )

    stmt = stmt.limit(limit + 1)
    rows = list((await db.execute(stmt)).scalars().all())

    next_cursor: str | None = None
    if sort == "created_at" and len(rows) > limit:
        rows = rows[:limit]
        last = rows[-1]
        next_cursor = encode_cursor(last.created_at, last.id)
    elif len(rows) > limit:
        # Other sorts don't support cursor pagination in v1; truncate without cursor.
        rows = rows[:limit]

    return rows, next_cursor


# ──────────────────────────────────────────────────────────────────────────────
# Mutations
# ──────────────────────────────────────────────────────────────────────────────


async def create_task(
    db: AsyncSession,
    *,
    actor: User,
    project_id: UUID,
    title: str,
    description: str | None,
    status: str | None,
    priority: str | None,
    assignee_id: UUID | None,
    due_date: date | None,
    label_ids: list[UUID] | None,
    request: Request | None = None,
) -> Task:
    # Validate dependencies.
    if assignee_id is not None:
        await _validate_assignee(
            db,
            workspace_id=actor.workspace_id,
            project_id=project_id,
            assignee_id=assignee_id,
        )
    if label_ids:
        await _validate_label_ids(db, workspace_id=actor.workspace_id, label_ids=label_ids)

    task = Task(
        project_id=project_id,
        workspace_id=actor.workspace_id,
        title=title,
        description=description,
        status=status or "backlog",
        priority=priority or "none",
        assignee_id=assignee_id,
        due_date=due_date,
        created_by=actor.id,
    )
    db.add(task)
    await db.flush()

    if label_ids:
        for lid in label_ids:
            db.add(TaskLabel(task_id=task.id, label_id=lid))

    await emit_activity(
        db,
        event_type="task.created",
        actor=actor,
        workspace_id=actor.workspace_id,
        project_id=project_id,
        subject_type="task",
        subject_id=task.id,
        metadata={"title": title},
        request=request,
    )
    if assignee_id is not None and assignee_id != actor.id:
        await emit_activity(
            db,
            event_type="task.assigned",
            actor=actor,
            workspace_id=actor.workspace_id,
            project_id=project_id,
            subject_type="task",
            subject_id=task.id,
            metadata={"assignee_id": str(assignee_id)},
            request=request,
        )
    if assignee_id is not None:
        from taskflow.services.notifications import dispatch_for_assignment

        await dispatch_for_assignment(
            db, actor=actor, task=task, new_assignee_id=assignee_id, request=request
        )

    if request is not None:
        from taskflow.realtime.after_commit import schedule_publish
        from taskflow.realtime.publish import publish_to_project

        payload = {
            "task_id": str(task.id),
            "project_id": str(project_id),
            "status": task.status,
        }
        schedule_publish(
            request,
            partial(
                publish_to_project,
                project_id=project_id,
                workspace_id=actor.workspace_id,
                event_type="task.created",
                payload=payload,
            ),
        )
    return task


async def update_task(
    db: AsyncSession,
    *,
    actor: User,
    task: Task,
    fields: dict[str, Any],
    label_ids: list[UUID] | None,
    label_ids_set: bool,
    request: Request | None = None,
) -> Task:
    """Apply field updates + label diff. `fields` carries only present keys."""
    prev_assignee = task.assignee_id

    if "assignee_id" in fields:
        new_assignee = cast(UUID | None, fields["assignee_id"])
        if new_assignee is not None:
            await _validate_assignee(
                db,
                workspace_id=actor.workspace_id,
                project_id=task.project_id,
                assignee_id=new_assignee,
            )
        task.assignee_id = new_assignee

    for key in ("title", "description", "priority", "due_date"):
        if key in fields:
            setattr(task, key, fields[key])

    if label_ids_set:
        await _validate_label_ids(db, workspace_id=actor.workspace_id, label_ids=label_ids or [])
        await db.execute(delete(TaskLabel).where(TaskLabel.task_id == task.id))
        for lid in label_ids or []:
            db.add(TaskLabel(task_id=task.id, label_id=lid))

    task.updated_at = datetime.now(UTC)

    # ADR 063 activity taxonomy doesn't include `task.updated`; only the
    # specific events below emit. Field-level changes are visible in the
    # task itself.

    if "assignee_id" in fields and fields["assignee_id"] != prev_assignee:
        if fields["assignee_id"] is None and prev_assignee is not None:
            await emit_activity(
                db,
                event_type="task.unassigned",
                actor=actor,
                workspace_id=actor.workspace_id,
                project_id=task.project_id,
                subject_type="task",
                subject_id=task.id,
                metadata={"was_assignee_id": str(prev_assignee)},
                request=request,
            )
        elif fields["assignee_id"] is not None:
            await emit_activity(
                db,
                event_type="task.assigned",
                actor=actor,
                workspace_id=actor.workspace_id,
                project_id=task.project_id,
                subject_type="task",
                subject_id=task.id,
                metadata={"assignee_id": str(fields["assignee_id"])},
                request=request,
            )
            from taskflow.services.notifications import dispatch_for_assignment

            await dispatch_for_assignment(
                db,
                actor=actor,
                task=task,
                new_assignee_id=fields["assignee_id"],
                request=request,
            )

    if request is not None:
        from taskflow.realtime.after_commit import schedule_publish
        from taskflow.realtime.publish import publish_to_project

        payload = {
            "task_id": str(task.id),
            "project_id": str(task.project_id),
            "status": task.status,
        }
        schedule_publish(
            request,
            partial(
                publish_to_project,
                project_id=task.project_id,
                workspace_id=actor.workspace_id,
                event_type="task.updated",
                payload=payload,
            ),
        )
    return task


async def change_status(
    db: AsyncSession,
    *,
    actor: User,
    task: Task,
    new_status: str,
    request: Request | None = None,
) -> Task:
    previous = task.status
    if previous == new_status:
        return task
    task.status = new_status
    task.updated_at = datetime.now(UTC)

    await emit_activity(
        db,
        event_type="task.status_changed",
        actor=actor,
        workspace_id=actor.workspace_id,
        project_id=task.project_id,
        subject_type="task",
        subject_id=task.id,
        metadata={"from": previous, "to": new_status},
        request=request,
    )

    from taskflow.services.notifications import dispatch_for_status_change

    await dispatch_for_status_change(
        db,
        actor=actor,
        task=task,
        previous_status=previous,
        new_status=new_status,
        request=request,
    )

    if request is not None:
        from taskflow.realtime.after_commit import schedule_publish
        from taskflow.realtime.publish import publish_to_project

        payload = {
            "task_id": str(task.id),
            "project_id": str(task.project_id),
            "from": previous,
            "to": new_status,
        }
        schedule_publish(
            request,
            partial(
                publish_to_project,
                project_id=task.project_id,
                workspace_id=actor.workspace_id,
                event_type="task.status_changed",
                payload=payload,
            ),
        )
    return task


# ──────────────────────────────────────────────────────────────────────────────
# Serializer (collected here so router stays thin)
# ──────────────────────────────────────────────────────────────────────────────


async def hydrate_task(db: AsyncSession, *, task: Task) -> dict[str, Any]:
    """Load assignee + labels + project name + comment count for a task DTO."""
    from taskflow.db.models.comment import Comment
    from taskflow.db.models.project import Project
    from taskflow.schemas.users import user_summary

    assignee = None
    if task.assignee_id is not None:
        a = await db.scalar(select(User).where(User.id == task.assignee_id))
        if a is not None:
            assignee = user_summary(a.id, a.name, deleted=a.deleted_at is not None)

    label_rows = await db.execute(
        select(Label)
        .join(TaskLabel, TaskLabel.label_id == Label.id)
        .where(TaskLabel.task_id == task.id)
        .order_by(Label.name.asc())
    )
    labels = list(label_rows.scalars().all())

    comment_count = (
        await db.scalar(select(func.count(Comment.id)).where(Comment.task_id == task.id))
    ) or 0

    project = await db.scalar(select(Project).where(Project.id == task.project_id))
    assert project is not None

    return {
        "task": task,
        "assignee": assignee,
        "labels": labels,
        "comment_count": int(comment_count),
        "project": project,
    }
