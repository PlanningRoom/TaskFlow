"""Phase C8 — dashboard endpoints (PRD §13)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


async def test_my_tasks_empty_when_no_assignments(http: AsyncClient) -> None:
    await signup_owner(http)
    r = await http.get("/api/v1/dashboard/my-tasks")
    assert r.status_code == 200
    assert r.json()["groups"] == []


async def test_my_tasks_groups_by_project(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    headers = csrf_headers(http)
    project = (await http.post("/api/v1/projects", json={"name": "P"}, headers=headers)).json()
    await http.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Mine", "assignee_id": str(owner.id)},
        headers=headers,
    )
    await http.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Not mine"},
        headers=headers,
    )
    r = await http.get("/api/v1/dashboard/my-tasks")
    body = r.json()
    assert len(body["groups"]) == 1
    titles = [t["title"] for t in body["groups"][0]["tasks"]]
    assert "Mine" in titles and "Not mine" not in titles


async def test_my_tasks_overdue_first(http: AsyncClient, db_session: AsyncSession) -> None:
    from datetime import date, timedelta

    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    headers = csrf_headers(http)
    project = (await http.post("/api/v1/projects", json={"name": "P"}, headers=headers)).json()
    pid = project["id"]
    overdue_due = (date.today() - timedelta(days=2)).isoformat()
    today_due = date.today().isoformat()
    await http.post(
        f"/api/v1/projects/{pid}/tasks",
        json={
            "title": "Today",
            "assignee_id": str(owner.id),
            "due_date": today_due,
        },
        headers=headers,
    )
    await http.post(
        f"/api/v1/projects/{pid}/tasks",
        json={
            "title": "Overdue",
            "assignee_id": str(owner.id),
            "due_date": overdue_due,
        },
        headers=headers,
    )
    r = await http.get("/api/v1/dashboard/my-tasks")
    titles = [t["title"] for t in r.json()["groups"][0]["tasks"]]
    assert titles[0] == "Overdue"
    assert titles[1] == "Today"


async def test_dashboard_projects_status_counts(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    project = (await http.post("/api/v1/projects", json={"name": "Aurora"}, headers=headers)).json()
    pid = project["id"]
    # 1 backlog (default), 1 in_progress.
    await http.post(f"/api/v1/projects/{pid}/tasks", json={"title": "A"}, headers=headers)
    t = (
        await http.post(f"/api/v1/projects/{pid}/tasks", json={"title": "B"}, headers=headers)
    ).json()
    await http.patch(
        f"/api/v1/tasks/{t['id']}/status",
        json={"status": "in_progress"},
        headers=headers,
    )
    r = await http.get("/api/v1/dashboard/projects")
    assert r.status_code == 200
    body = r.json()
    proj = next(p for p in body["projects"] if p["name"] == "Aurora")
    assert proj["task_counts"]["backlog"] == 1
    assert proj["task_counts"]["in_progress"] == 1
    assert proj["task_counts"]["done"] == 0


async def test_member_only_sees_accessible_projects(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    await http.post("/api/v1/projects", json={"name": "Owner-only"}, headers=headers)

    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    async with auth_client(app, db_session, member) as client:
        r = await client.get("/api/v1/dashboard/projects")
        assert r.status_code == 200
        assert r.json()["projects"] == []
