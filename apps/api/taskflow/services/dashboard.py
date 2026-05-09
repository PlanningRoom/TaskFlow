"""Dashboard query service (PRD §13)."""

from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.permissions import has_implicit_project_access
from taskflow.db.models.project import Project, ProjectMembership
from taskflow.db.models.task import Task
from taskflow.db.models.user import User


async def my_tasks(db: AsyncSession, *, user: User) -> list[tuple[Project, list[Task]]]:
    """Return (project, tasks) groups for tasks assigned to `user`.

    Excludes done/cancelled. Ordered overdue/soonest first (NULLs last).
    """
    rows = await db.execute(
        select(Task, Project)
        .join(Project, Project.id == Task.project_id)
        .where(
            Task.workspace_id == user.workspace_id,
            Task.assignee_id == user.id,
            Task.status.notin_(("done", "cancelled")),
        )
        .order_by(
            Task.due_date.is_(None).asc(),
            Task.due_date.asc(),
            Task.created_at.asc(),
        )
    )
    grouped: dict[UUID, tuple[Project, list[Task]]] = {}
    for task, project in rows.all():
        if project.id not in grouped:
            grouped[project.id] = (project, [])
        grouped[project.id][1].append(task)
    return list(grouped.values())


async def projects_with_counts(
    db: AsyncSession, *, user: User
) -> list[tuple[Project, dict[str, int]]]:
    """Visible projects + task-count breakdowns by status."""
    if has_implicit_project_access(user.role):
        proj_stmt = (
            select(Project)
            .where(Project.workspace_id == user.workspace_id)
            .order_by(Project.name.asc())
        )
    else:
        proj_stmt = (
            select(Project)
            .join(ProjectMembership, ProjectMembership.project_id == Project.id)
            .where(
                Project.workspace_id == user.workspace_id,
                ProjectMembership.user_id == user.id,
            )
            .order_by(Project.name.asc())
        )

    projects = list((await db.execute(proj_stmt)).scalars().all())
    if not projects:
        return []

    project_ids = [p.id for p in projects]
    rows = await db.execute(
        select(Task.project_id, Task.status, func.count(Task.id))
        .where(Task.project_id.in_(project_ids))
        .group_by(Task.project_id, Task.status)
    )
    counts: dict[UUID, dict[str, int]] = defaultdict(dict)
    for project_id, status, count in rows.all():
        counts[project_id][status] = count

    return [(p, counts.get(p.id, {})) for p in projects]
