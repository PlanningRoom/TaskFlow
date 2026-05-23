"""Phase E4 — seed script idempotency + output shape."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.comment import Comment
from taskflow.db.models.label import Label
from taskflow.db.models.notification import Notification
from taskflow.db.models.project import Project
from taskflow.db.models.task import Task
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace
from taskflow.scripts.seed import (
    COMMENTS,
    PROJECTS,
    TASKS,
    USERS,
    WORKSPACE_NAME,
    seed,
)

pytestmark = pytest.mark.asyncio


async def test_seed_produces_expected_shape(db_session: AsyncSession) -> None:
    created = await seed()
    assert created == len(TASKS)

    workspace = await db_session.scalar(select(Workspace).where(Workspace.name == WORKSPACE_NAME))
    assert workspace is not None
    assert workspace.created_by is not None  # back-patched to the Owner.

    user_count = await db_session.scalar(
        select(func.count()).select_from(User).where(User.workspace_id == workspace.id)
    )
    assert user_count == len(USERS)

    project_count = await db_session.scalar(
        select(func.count()).select_from(Project).where(Project.workspace_id == workspace.id)
    )
    assert project_count == len(PROJECTS)

    task_count = await db_session.scalar(
        select(func.count()).select_from(Task).where(Task.workspace_id == workspace.id)
    )
    assert task_count == len(TASKS)

    label_count = await db_session.scalar(
        select(func.count()).select_from(Label).where(Label.workspace_id == workspace.id)
    )
    assert label_count == 8  # one per palette colour

    comment_count = await db_session.scalar(select(func.count()).select_from(Comment))
    assert comment_count == len(COMMENTS)


async def test_seed_status_and_priority_spread(db_session: AsyncSession) -> None:
    await seed()
    rows = (
        await db_session.execute(
            select(Task.status, Task.priority)
            .join(Workspace, Task.workspace_id == Workspace.id)
            .where(Workspace.name == WORKSPACE_NAME)
        )
    ).all()
    statuses = {r.status for r in rows}
    priorities = {r.priority for r in rows}
    # The seed exercises every status (incl. cancelled) and every priority.
    assert statuses == {"backlog", "todo", "in_progress", "in_review", "done", "cancelled"}
    assert priorities == {"none", "low", "medium", "high", "urgent"}


async def test_seed_creates_notifications_for_mentioned_members(
    db_session: AsyncSession,
) -> None:
    await seed()
    workspace = await db_session.scalar(select(Workspace).where(Workspace.name == WORKSPACE_NAME))
    assert workspace is not None

    dev1 = await db_session.scalar(
        select(User).where(User.email == "dev1@aurora.test", User.workspace_id == workspace.id)
    )
    assert dev1 is not None

    n_for_dev1 = await db_session.scalar(
        select(func.count()).select_from(Notification).where(Notification.recipient_id == dev1.id)
    )
    # Several COMMENTS mention @dev1 — at least one notification should exist.
    assert (n_for_dev1 or 0) >= 1


async def test_seed_is_idempotent(db_session: AsyncSession) -> None:
    first = await seed()
    assert first == len(TASKS)

    snapshot_users = await db_session.scalar(select(func.count()).select_from(User))
    snapshot_tasks = await db_session.scalar(select(func.count()).select_from(Task))

    second = await seed()
    assert second == 0  # short-circuited

    again_users = await db_session.scalar(select(func.count()).select_from(User))
    again_tasks = await db_session.scalar(select(func.count()).select_from(Task))

    assert snapshot_users == again_users
    assert snapshot_tasks == again_tasks
