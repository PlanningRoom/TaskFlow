"""Phase C5 — activity feed endpoints (PRD §13.2 / §14, ADR 063)."""

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


async def _bootstrap(http: AsyncClient) -> tuple[str, str]:
    """Sign-up, create project + task, return (project_id, task_id)."""
    await signup_owner(http)
    headers = csrf_headers(http)
    project = (await http.post("/api/v1/projects", json={"name": "P"}, headers=headers)).json()
    task = (
        await http.post(
            f"/api/v1/projects/{project['id']}/tasks",
            json={"title": "T"},
            headers=headers,
        )
    ).json()
    return str(project["id"]), str(task["id"])


async def test_workspace_feed_includes_task_created(http: AsyncClient) -> None:
    await _bootstrap(http)
    response = await http.get("/api/v1/activity")
    assert response.status_code == 200
    types = [e["event_type"] for e in response.json()["events"]]
    assert "task.created" in types


async def test_workspace_feed_includes_status_change_and_comment(
    http: AsyncClient,
) -> None:
    project_id, task_id = await _bootstrap(http)
    headers = csrf_headers(http)
    await http.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=headers,
    )
    await http.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"body": "thoughts"},
        headers=headers,
    )
    response = await http.get("/api/v1/activity")
    types = {e["event_type"] for e in response.json()["events"]}
    assert "task.status_changed" in types
    assert "comment.created" in types


async def test_project_scope_requires_visibility(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    project_id, _ = await _bootstrap(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(
        db_session, workspace_id=owner.workspace_id, role="member", email="m@x.com"
    )
    async with auth_client(app, db_session, member) as client:
        r = await client.get(f"/api/v1/activity?project_id={project_id}")
        assert r.status_code == 403


async def test_workspace_feed_filters_for_member(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    project_id, task_id = await _bootstrap(http)  # Owner's workspace
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(
        db_session, workspace_id=owner.workspace_id, role="member", email="m@x.com"
    )
    # Member has no access to Owner's project; workspace feed should hide events.
    async with auth_client(app, db_session, member) as client:
        r = await client.get("/api/v1/activity")
        assert r.status_code == 200
        assert r.json()["events"] == []


async def test_cross_workspace_project_scope_404(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    project_id, _ = await _bootstrap(http)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as b_http:
        await signup_owner(
            b_http,
            payload={
                "email": "b@example.com",
                "password": "correct-horse-battery-staple-b",
                "display_name": "B",
                "workspace_name": "B",
            },
        )
        r = await b_http.get(f"/api/v1/activity?project_id={project_id}")
        assert r.status_code == 404


async def test_owner_project_scoped_feed(http: AsyncClient) -> None:
    project_id, _ = await _bootstrap(http)
    # Owner has implicit visibility; project scope filters to that project.
    r = await http.get(f"/api/v1/activity?project_id={project_id}")
    assert r.status_code == 200
    types = {e["event_type"] for e in r.json()["events"]}
    assert "task.created" in types


async def test_activity_feed_cursor_pagination(http: AsyncClient) -> None:
    project_id, _ = await _bootstrap(http)
    headers = csrf_headers(http)
    # Generate several activity rows (each status change emits one).
    for status in ("in_progress", "in_review", "done"):
        task = (
            await http.post(
                f"/api/v1/projects/{project_id}/tasks",
                json={"title": f"task-{status}"},
                headers=headers,
            )
        ).json()
        await http.patch(
            f"/api/v1/tasks/{task['id']}/status",
            json={"status": status},
            headers=headers,
        )

    first = await http.get("/api/v1/activity?limit=2")
    body = first.json()
    assert len(body["events"]) == 2
    assert body["next_cursor"]

    second = await http.get(f"/api/v1/activity?limit=2&cursor={body['next_cursor']}")
    assert second.status_code == 200
    assert len(second.json()["events"]) >= 1


async def test_activity_feed_ignores_malformed_cursor(http: AsyncClient) -> None:
    await _bootstrap(http)
    # A malformed cursor decodes to None and is silently ignored (no 500).
    r = await http.get("/api/v1/activity?cursor=!!!not-base64!!!")
    assert r.status_code == 200
    assert any(e["event_type"] == "task.created" for e in r.json()["events"])


async def test_get_event_direct_lookup_and_missing(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    from uuid import uuid4

    from taskflow.db.models.activity_event import ActivityEvent
    from taskflow.errors import NotFoundError
    from taskflow.services import activity as activity_service

    await _bootstrap(http)
    created = await db_session.scalar(
        select(ActivityEvent).where(ActivityEvent.event_type == "task.created")
    )
    assert created is not None

    fetched = await activity_service.get_event(db_session, event_id=created.id)
    assert fetched.id == created.id

    with pytest.raises(NotFoundError):
        await activity_service.get_event(db_session, event_id=uuid4())
