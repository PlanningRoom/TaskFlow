"""Phase C3 — task CRUD endpoints (PRD §6, ADR 008/040/062)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.activity_event import ActivityEvent
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


async def _make_project(http: AsyncClient, name: str = "P") -> str:
    body = (
        await http.post("/api/v1/projects", json={"name": name}, headers=csrf_headers(http))
    ).json()
    return str(body["id"])


async def test_owner_can_create_task(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    response = await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Fix the thing", "priority": "high"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["title"] == "Fix the thing"
    assert body["status"] == "backlog"
    assert body["priority"] == "high"

    activity = await db_session.scalar(
        select(ActivityEvent).where(ActivityEvent.event_type == "task.created")
    )
    assert activity is not None


async def test_viewer_cannot_create_task(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    viewer = await make_user(
        db_session, workspace_id=owner.workspace_id, role="viewer", email="v@x.com"
    )
    async with auth_client(app, db_session, viewer) as client:
        r = await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Forbidden"},
            headers=csrf_headers(client),
        )
        assert r.status_code == 403


async def test_create_task_with_label(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    label = (
        await http.post(
            "/api/v1/labels",
            json={"name": "bug", "color": "red"},
            headers=csrf_headers(http),
        )
    ).json()
    response = await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T", "label_ids": [label["id"]]},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["labels"]) == 1
    assert body["labels"][0]["name"] == "bug"


async def test_create_task_invalid_assignee_outside_workspace(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    from uuid import uuid4

    response = await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T", "assignee_id": str(uuid4())},
        headers=csrf_headers(http),
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_ASSIGNEE"


async def test_create_task_assignee_without_project_access(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    response = await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T", "assignee_id": str(member.id)},
        headers=csrf_headers(http),
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_ASSIGNEE"


async def test_get_task_cross_workspace_404(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    # Owner A creates a task in their workspace.
    await signup_owner(http)
    project_id = await _make_project(http)
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Secret"},
            headers=csrf_headers(http),
        )
    ).json()

    # Owner B (separate workspace) tries to read it.
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
        response = await b_http.get(f"/api/v1/tasks/{task['id']}")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "TASK_NOT_FOUND"


async def test_update_task_emits_assignment_change(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "T"},
            headers=csrf_headers(http),
        )
    ).json()

    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None

    # Assign to owner (admin/owner has implicit project access).
    r = await http.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"assignee_id": str(owner.id)},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200
    assigned = await db_session.scalar(
        select(ActivityEvent).where(ActivityEvent.event_type == "task.assigned")
    )
    assert assigned is not None

    # Unassign.
    r2 = await http.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"assignee_id": None},
        headers=csrf_headers(http),
    )
    assert r2.status_code == 200
    unassigned = await db_session.scalar(
        select(ActivityEvent).where(ActivityEvent.event_type == "task.unassigned")
    )
    assert unassigned is not None


async def test_status_split_endpoint_emits_event(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "T"},
            headers=csrf_headers(http),
        )
    ).json()
    r = await http.patch(
        f"/api/v1/tasks/{task['id']}/status",
        json={"status": "in_progress"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"

    activity = await db_session.scalar(
        select(ActivityEvent).where(ActivityEvent.event_type == "task.status_changed")
    )
    assert activity is not None
    assert activity.metadata_["from"] == "backlog"
    assert activity.metadata_["to"] == "in_progress"


async def test_list_tasks_excludes_cancelled_by_default(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    # 1 backlog + 1 cancelled.
    headers = csrf_headers(http)
    await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Active"},
        headers=headers,
    )
    cancelled = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Cancelled"},
            headers=headers,
        )
    ).json()
    await http.patch(
        f"/api/v1/tasks/{cancelled['id']}/status",
        json={"status": "cancelled"},
        headers=headers,
    )

    r = await http.get(f"/api/v1/projects/{project_id}/tasks")
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()["tasks"]]
    assert "Active" in titles and "Cancelled" not in titles

    r2 = await http.get(f"/api/v1/projects/{project_id}/tasks?include_cancelled=true")
    titles2 = [t["title"] for t in r2.json()["tasks"]]
    assert "Cancelled" in titles2


async def test_label_assignment_full_replacement(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    project_id = await _make_project(http)
    bug = (
        await http.post("/api/v1/labels", json={"name": "bug", "color": "red"}, headers=headers)
    ).json()
    feature = (
        await http.post(
            "/api/v1/labels", json={"name": "feature", "color": "green"}, headers=headers
        )
    ).json()
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "T", "label_ids": [bug["id"]]},
            headers=headers,
        )
    ).json()
    assert {lbl["name"] for lbl in task["labels"]} == {"bug"}

    # PATCH replaces the set.
    r = await http.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"label_ids": [feature["id"]]},
        headers=headers,
    )
    assert r.status_code == 200
    assert {lbl["name"] for lbl in r.json()["labels"]} == {"feature"}

    # Empty list clears.
    r2 = await http.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"label_ids": []},
        headers=headers,
    )
    assert r2.json()["labels"] == []


async def test_fts_search_vector_updated(http: AsyncClient, db_session: AsyncSession) -> None:
    """Verify the GENERATED `search_vector` column is populated and updates."""
    from sqlalchemy import text

    await signup_owner(http)
    project_id = await _make_project(http)
    headers = csrf_headers(http)
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Fix authentication bug", "description": "It's broken"},
            headers=headers,
        )
    ).json()

    found = await db_session.execute(
        text("SELECT id FROM tasks WHERE search_vector @@ websearch_to_tsquery('english', :q)"),
        {"q": "authentication"},
    )
    rows = list(found.scalars().all())
    assert task["id"] in {str(r) for r in rows}

    await http.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"title": "Renamed completely"},
        headers=headers,
    )
    found2 = await db_session.execute(
        text("SELECT id FROM tasks WHERE search_vector @@ websearch_to_tsquery('english', :q)"),
        {"q": "renamed"},
    )
    rows2 = list(found2.scalars().all())
    assert task["id"] in {str(r) for r in rows2}
