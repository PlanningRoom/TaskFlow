"""Phase C6 — notification endpoints + dispatch (PRD §15.1, ADR 064/070)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.notification import Notification
from taskflow.db.models.user import User
from taskflow.settings import settings
from tests.integration._helpers import (
    auth_client,
    csrf_headers,
    make_user,
    signup_owner,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def app(db_engine: None) -> FastAPI:
    settings.cookie_secure = False
    from taskflow.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
async def http(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


async def _setup_owner_and_member(
    http: AsyncClient, db_session: AsyncSession
) -> tuple[User, User, str]:
    """Owner signs up and creates a project; admin member is added; returns
    (owner, admin, project_id). Admin has implicit project access."""
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    admin = await make_user(
        db_session,
        workspace_id=owner.workspace_id,
        role="admin",
        email="admin@example.com",
        name="Adam Admin",
    )
    project = (
        await http.post(
            "/api/v1/projects",
            json={"name": "Aurora"},
            headers=csrf_headers(http),
        )
    ).json()
    return owner, admin, str(project["id"])


async def test_assignment_notification(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    owner, admin, project_id = await _setup_owner_and_member(http, db_session)
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "T", "assignee_id": str(admin.id)},
            headers=csrf_headers(http),
        )
    ).json()
    notif = await db_session.scalar(
        select(Notification).where(
            Notification.recipient_id == admin.id,
            Notification.event_type == "task_assigned",
        )
    )
    assert notif is not None
    assert notif.task_id is not None and str(notif.task_id) == task["id"]


async def test_self_assignment_suppressed(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    owner, admin, project_id = await _setup_owner_and_member(http, db_session)
    await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T", "assignee_id": str(owner.id)},
        headers=csrf_headers(http),
    )
    notif = await db_session.scalar(
        select(Notification).where(Notification.recipient_id == owner.id)
    )
    assert notif is None


async def test_status_change_notifies_assignee(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    owner, admin, project_id = await _setup_owner_and_member(http, db_session)
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "T", "assignee_id": str(admin.id)},
            headers=csrf_headers(http),
        )
    ).json()
    # Owner moves to in_progress; admin (assignee) gets a notification.
    await http.patch(
        f"/api/v1/tasks/{task['id']}/status",
        json={"status": "in_progress"},
        headers=csrf_headers(http),
    )
    rows = list(
        (
            await db_session.execute(
                select(Notification).where(
                    Notification.recipient_id == admin.id,
                    Notification.event_type == "task_status_changed",
                )
            )
        ).scalars()
    )
    assert len(rows) == 1


async def test_mention_dedup_with_assignment(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    owner, admin, project_id = await _setup_owner_and_member(http, db_session)
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "T", "assignee_id": str(admin.id)},
            headers=csrf_headers(http),
        )
    ).json()
    # Clear existing assignment notification so we count only comment dispatch.
    await db_session.execute(select(Notification).where(Notification.recipient_id == admin.id))
    # Owner posts a comment that mentions admin (the assignee).
    await http.post(
        f"/api/v1/tasks/{task['id']}/comments",
        json={"body": "Hi @adam-admin"},
        headers=csrf_headers(http),
    )
    notifs = list(
        (
            await db_session.execute(
                select(Notification).where(
                    Notification.recipient_id == admin.id,
                    Notification.task_id == task["id"],
                )
            )
        ).scalars()
    )
    # One assignment + one mention; NOT a separate task_commented for the assignee
    # because the mention wins.
    types = sorted(n.event_type for n in notifs)
    assert types == ["mention", "task_assigned"]


async def test_unread_count_and_mark_all_read(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    owner, admin, project_id = await _setup_owner_and_member(http, db_session)
    await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T", "assignee_id": str(admin.id)},
        headers=csrf_headers(http),
    )
    async with auth_client(app, db_session, admin) as client:
        unread = await client.get("/api/v1/notifications/unread-count")
        assert unread.json()["count"] == 1

        listed = await client.get("/api/v1/notifications")
        assert len(listed.json()["notifications"]) == 1

        # Mark all read.
        ack = await client.post(
            "/api/v1/notifications/mark-all-read",
            headers=csrf_headers(client),
        )
        assert ack.status_code == 200

        unread2 = await client.get("/api/v1/notifications/unread-count")
        assert unread2.json()["count"] == 0


async def test_mark_one_read_scoped_to_recipient(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    owner, admin, project_id = await _setup_owner_and_member(http, db_session)
    await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T", "assignee_id": str(admin.id)},
        headers=csrf_headers(http),
    )
    notif = await db_session.scalar(
        select(Notification).where(Notification.recipient_id == admin.id)
    )
    assert notif is not None
    # Owner attempts to read admin's notification.
    bad = await http.post(f"/api/v1/notifications/{notif.id}/read", headers=csrf_headers(http))
    assert bad.status_code == 404


async def test_self_mention_in_comment_suppressed(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    owner, admin, project_id = await _setup_owner_and_member(http, db_session)
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "T"},  # unassigned → no assignee notification either
            headers=csrf_headers(http),
        )
    ).json()
    # Owner mentions themselves ("Aurora Owner" → @aurora-owner).
    await http.post(
        f"/api/v1/tasks/{task['id']}/comments",
        json={"body": "Note to self @aurora-owner"},
        headers=csrf_headers(http),
    )
    owner_notif = await db_session.scalar(
        select(Notification).where(Notification.recipient_id == owner.id)
    )
    assert owner_notif is None


async def test_mark_one_read_success(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    owner, admin, project_id = await _setup_owner_and_member(http, db_session)
    await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T", "assignee_id": str(admin.id)},
        headers=csrf_headers(http),
    )
    notif = await db_session.scalar(
        select(Notification).where(Notification.recipient_id == admin.id)
    )
    assert notif is not None and notif.read_at is None

    async with auth_client(app, db_session, admin) as client:
        r = await client.post(
            f"/api/v1/notifications/{notif.id}/read", headers=csrf_headers(client)
        )
        assert r.status_code == 200, r.text

    refreshed = await db_session.get(Notification, notif.id, populate_existing=True)
    assert refreshed is not None and refreshed.read_at is not None


async def test_notifications_list_cursor_pagination(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    owner, admin, project_id = await _setup_owner_and_member(http, db_session)
    # Three assignments → three notifications for admin.
    for i in range(3):
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": f"T{i}", "assignee_id": str(admin.id)},
            headers=csrf_headers(http),
        )

    async with auth_client(app, db_session, admin) as client:
        first = await client.get("/api/v1/notifications?limit=2")
        body = first.json()
        assert len(body["notifications"]) == 2
        assert body["next_cursor"]

        second = await client.get(f"/api/v1/notifications?limit=2&cursor={body['next_cursor']}")
        page2 = second.json()
        assert len(page2["notifications"]) == 1
        assert page2["next_cursor"] is None
