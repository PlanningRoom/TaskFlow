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


async def test_create_task_rejects_unknown_label(http: AsyncClient) -> None:
    from uuid import uuid4

    await signup_owner(http)
    project_id = await _make_project(http)
    response = await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T", "label_ids": [str(uuid4())]},
        headers=csrf_headers(http),
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_LABEL"


async def test_status_change_to_same_status_is_noop(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    task = (
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "T"},  # defaults to backlog
            headers=csrf_headers(http),
        )
    ).json()

    r = await http.patch(
        f"/api/v1/tasks/{task['id']}/status",
        json={"status": "backlog"},  # same as current
        headers=csrf_headers(http),
    )
    assert r.status_code == 200
    # No status_changed activity row written for a no-op transition.
    events = (
        await db_session.execute(
            select(ActivityEvent).where(ActivityEvent.event_type == "task.status_changed")
        )
    ).all()
    assert events == []


async def test_list_tasks_due_filters(http: AsyncClient) -> None:
    from datetime import date, timedelta

    await signup_owner(http)
    project_id = await _make_project(http)
    headers = csrf_headers(http)
    today = date.today()

    async def _mk(title: str, due: date | None) -> None:
        payload: dict[str, object] = {"title": title}
        if due is not None:
            payload["due_date"] = due.isoformat()
        await http.post(f"/api/v1/projects/{project_id}/tasks", json=payload, headers=headers)

    await _mk("Overdue", today - timedelta(days=2))
    await _mk("Today", today)
    await _mk("ThisWeek", today + timedelta(days=3))
    await _mk("NoDue", None)

    async def _titles(query: str) -> set[str]:
        r = await http.get(f"/api/v1/projects/{project_id}/tasks?{query}")
        assert r.status_code == 200, r.text
        return {t["title"] for t in r.json()["tasks"]}

    assert "Overdue" in await _titles("due=overdue")
    assert "Today" in await _titles("due=today")
    assert "ThisWeek" in await _titles("due=this_week")
    assert "NoDue" in await _titles("due=no_due_date")
    # Unknown due value falls through to no filter (all four returned).
    assert len(await _titles("due=bogus")) == 4


async def test_list_tasks_sort_variants_and_filters(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    headers = csrf_headers(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None

    await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Urgent", "priority": "urgent", "assignee_id": str(owner.id)},
        headers=headers,
    )
    await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Low", "priority": "low"},
        headers=headers,
    )

    # Each sort key exercises a distinct ORDER BY branch.
    for sort in ("priority", "due_date", "assignee", "created_at"):
        r = await http.get(f"/api/v1/projects/{project_id}/tasks?sort={sort}")
        assert r.status_code == 200, r.text
        assert len(r.json()["tasks"]) == 2

    # priority sort puts "urgent" before "low".
    ranked = await http.get(f"/api/v1/projects/{project_id}/tasks?sort=priority")
    assert [t["title"] for t in ranked.json()["tasks"]] == ["Urgent", "Low"]

    # assignee + priority + status filters each narrow the set.
    assigned = await http.get(f"/api/v1/projects/{project_id}/tasks?assignee={owner.id}")
    assert {t["title"] for t in assigned.json()["tasks"]} == {"Urgent"}
    high = await http.get(f"/api/v1/projects/{project_id}/tasks?priority=urgent")
    assert {t["title"] for t in high.json()["tasks"]} == {"Urgent"}
    backlog = await http.get(f"/api/v1/projects/{project_id}/tasks?status=backlog")
    assert {t["title"] for t in backlog.json()["tasks"]} == {"Urgent", "Low"}


async def test_list_tasks_filter_by_label(http: AsyncClient) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    headers = csrf_headers(http)
    label = (
        await http.post("/api/v1/labels", json={"name": "bug", "color": "red"}, headers=headers)
    ).json()
    await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Labelled", "label_ids": [label["id"]]},
        headers=headers,
    )
    await http.post(
        f"/api/v1/projects/{project_id}/tasks", json={"title": "Plain"}, headers=headers
    )

    r = await http.get(f"/api/v1/projects/{project_id}/tasks?label={label['id']}")
    assert r.status_code == 200
    assert {t["title"] for t in r.json()["tasks"]} == {"Labelled"}


async def test_create_task_assigned_to_another_member_emits_and_notifies(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None

    # A member who is granted access to the project, then assigned a task.
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    await http.post(
        f"/api/v1/projects/{project_id}/access",
        json={"user_id": str(member.id)},
        headers=csrf_headers(http),
    )

    r = await http.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "For member", "assignee_id": str(member.id)},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # Assigning to someone other than the actor emits a task.assigned activity row.
    assigned = await db_session.scalar(
        select(ActivityEvent).where(ActivityEvent.event_type == "task.assigned")
    )
    assert assigned is not None


async def test_list_tasks_cursor_pagination(http: AsyncClient) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    headers = csrf_headers(http)
    for i in range(3):
        await http.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": f"T{i}"},
            headers=headers,
        )

    # created_at sort + limit < count → a next_cursor is returned.
    first = await http.get(f"/api/v1/projects/{project_id}/tasks?limit=2&sort=created_at")
    body = first.json()
    assert len(body["tasks"]) == 2
    assert body["next_cursor"]

    # Following the cursor returns the remaining task.
    second = await http.get(
        f"/api/v1/projects/{project_id}/tasks?limit=2&sort=created_at&cursor={body['next_cursor']}"
    )
    page2 = second.json()
    assert len(page2["tasks"]) == 1
    assert page2["next_cursor"] is None

    # Non-created_at sort truncates to the limit without offering a cursor.
    other = await http.get(f"/api/v1/projects/{project_id}/tasks?limit=2&sort=priority")
    other_body = other.json()
    assert len(other_body["tasks"]) == 2
    assert other_body["next_cursor"] is None


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
