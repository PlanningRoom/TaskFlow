"""Cross-workspace isolation sweep (ADR 003 / TDD §8.3).

Foundational sweep that asserts a user in workspace A cannot see or affect
data in workspace B even with the correct UUID. Re-extended in C3/C4 with
per-domain cases.
"""

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


async def _setup_two_workspaces(app: FastAPI, db_session: AsyncSession) -> tuple[User, User]:
    """Create two unrelated workspaces (A and B), return their owners."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as a:
        await signup_owner(
            a,
            payload={
                "email": "owner-a@example.com",
                "password": "correct-horse-battery-staple-a",
                "display_name": "Owner A",
                "workspace_name": "Workspace A",
            },
        )
    async with AsyncClient(transport=transport, base_url="http://testserver") as b:
        await signup_owner(
            b,
            payload={
                "email": "owner-b@example.com",
                "password": "correct-horse-battery-staple-b",
                "display_name": "Owner B",
                "workspace_name": "Workspace B",
            },
        )

    owner_a = await db_session.scalar(select(User).where(User.email == "owner-a@example.com"))
    owner_b = await db_session.scalar(select(User).where(User.email == "owner-b@example.com"))
    assert owner_a is not None and owner_b is not None
    return owner_a, owner_b


async def test_cannot_read_project_in_other_workspace(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)

    # Owner B creates a project in workspace B.
    async with auth_client(app, db_session, owner_b) as b_client:
        b_project = (
            await b_client.post(
                "/api/v1/projects",
                json={"name": "B's secret"},
                headers=csrf_headers(b_client),
            )
        ).json()

    # Owner A tries to read it — 404 (existence not disclosed).
    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.get(f"/api/v1/projects/{b_project['id']}")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "PROJECT_NOT_FOUND"


async def test_cannot_update_project_in_other_workspace(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    async with auth_client(app, db_session, owner_b) as b_client:
        b_project = (
            await b_client.post(
                "/api/v1/projects",
                json={"name": "B"},
                headers=csrf_headers(b_client),
            )
        ).json()

    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.patch(
            f"/api/v1/projects/{b_project['id']}",
            json={"name": "stolen"},
            headers=csrf_headers(a_client),
        )
        assert response.status_code == 404


async def test_cannot_grant_access_to_user_in_other_workspace(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)

    async with auth_client(app, db_session, owner_a) as a_client:
        a_project = (
            await a_client.post(
                "/api/v1/projects",
                json={"name": "A's project"},
                headers=csrf_headers(a_client),
            )
        ).json()

        response = await a_client.post(
            f"/api/v1/projects/{a_project['id']}/access",
            json={"user_id": str(owner_b.id)},
            headers=csrf_headers(a_client),
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "USER_NOT_FOUND"


async def test_member_list_isolated(app: FastAPI, db_session: AsyncSession) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.get("/api/v1/workspaces/me/members")
        assert response.status_code == 200
        members = response.json()["members"]
        assert len(members) == 1
        assert members[0]["email"] == "owner-a@example.com"


async def test_label_list_isolated(app: FastAPI, db_session: AsyncSession) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    async with auth_client(app, db_session, owner_b) as b_client:
        await b_client.post(
            "/api/v1/labels",
            json={"name": "secret-b", "color": "red"},
            headers=csrf_headers(b_client),
        )

    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.get("/api/v1/labels")
        assert response.status_code == 200
        assert response.json()["labels"] == []


# ─────────────────────────────────────────────────────────────────────────────
# Phase E3 — extended sweep
# Each test asserts: caller in workspace A cannot read, modify, or otherwise
# affect a resource in workspace B, even with a known UUID. 404 is preferred
# over 403 — existence shouldn't be disclosed.
# ─────────────────────────────────────────────────────────────────────────────


async def _create_b_project_and_task(
    app: FastAPI, db_session: AsyncSession, owner_b: User
) -> tuple[str, str]:
    """Create a project + task in workspace B, return their ids."""
    async with auth_client(app, db_session, owner_b) as b_client:
        project = (
            await b_client.post(
                "/api/v1/projects",
                json={"name": "B's project"},
                headers=csrf_headers(b_client),
            )
        ).json()
        task = (
            await b_client.post(
                f"/api/v1/projects/{project['id']}/tasks",
                json={"title": "B's secret task"},
                headers=csrf_headers(b_client),
            )
        ).json()
    return project["id"], task["id"]


async def test_project_list_excludes_other_workspace(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    await _create_b_project_and_task(app, db_session, owner_b)

    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.get("/api/v1/projects")
        assert response.status_code == 200
        assert response.json()["projects"] == []


async def test_cannot_read_task_in_other_workspace(app: FastAPI, db_session: AsyncSession) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    _, b_task_id = await _create_b_project_and_task(app, db_session, owner_b)

    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.get(f"/api/v1/tasks/{b_task_id}")
        assert response.status_code == 404


async def test_cannot_update_task_in_other_workspace(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    _, b_task_id = await _create_b_project_and_task(app, db_session, owner_b)

    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.patch(
            f"/api/v1/tasks/{b_task_id}",
            json={"title": "stolen title"},
            headers=csrf_headers(a_client),
        )
        assert response.status_code == 404
        status_resp = await a_client.patch(
            f"/api/v1/tasks/{b_task_id}/status",
            json={"status": "done"},
            headers=csrf_headers(a_client),
        )
        assert status_resp.status_code == 404


async def test_cannot_list_tasks_in_other_workspace_project(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    b_project_id, _ = await _create_b_project_and_task(app, db_session, owner_b)

    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.get(f"/api/v1/projects/{b_project_id}/tasks")
        assert response.status_code == 404


async def test_cannot_comment_on_task_in_other_workspace(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    _, b_task_id = await _create_b_project_and_task(app, db_session, owner_b)

    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.get(f"/api/v1/tasks/{b_task_id}/comments")
        assert response.status_code == 404
        post = await a_client.post(
            f"/api/v1/tasks/{b_task_id}/comments",
            json={"body": "intrusion"},
            headers=csrf_headers(a_client),
        )
        assert post.status_code == 404


async def test_search_excludes_other_workspace_tasks(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    await _create_b_project_and_task(app, db_session, owner_b)

    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.get("/api/v1/search", params={"q": "secret"})
        assert response.status_code == 200
        assert response.json()["results"] == []


async def test_activity_excludes_other_workspace(app: FastAPI, db_session: AsyncSession) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    await _create_b_project_and_task(app, db_session, owner_b)

    async with auth_client(app, db_session, owner_a) as a_client:
        response = await a_client.get("/api/v1/activity")
        assert response.status_code == 200
        # A's feed contains only events from workspace A — B's task.created is excluded.
        for event in response.json()["events"]:
            assert event["actor"]["id"] == str(owner_a.id)


async def test_dashboard_excludes_other_workspace(app: FastAPI, db_session: AsyncSession) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    await _create_b_project_and_task(app, db_session, owner_b)

    async with auth_client(app, db_session, owner_a) as a_client:
        my_tasks = await a_client.get("/api/v1/dashboard/my-tasks")
        assert my_tasks.status_code == 200
        assert my_tasks.json()["groups"] == []
        projects = await a_client.get("/api/v1/dashboard/projects")
        assert projects.status_code == 200
        assert projects.json()["projects"] == []


async def test_cannot_modify_label_in_other_workspace(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    async with auth_client(app, db_session, owner_b) as b_client:
        label = (
            await b_client.post(
                "/api/v1/labels",
                json={"name": "b-label", "color": "blue"},
                headers=csrf_headers(b_client),
            )
        ).json()

    async with auth_client(app, db_session, owner_a) as a_client:
        patch = await a_client.patch(
            f"/api/v1/labels/{label['id']}",
            json={"name": "stolen"},
            headers=csrf_headers(a_client),
        )
        assert patch.status_code == 404
        delete = await a_client.delete(
            f"/api/v1/labels/{label['id']}",
            headers=csrf_headers(a_client),
        )
        assert delete.status_code == 404


async def test_workspace_update_only_touches_caller_workspace(
    app: FastAPI, db_session: AsyncSession
) -> None:
    owner_a, owner_b = await _setup_two_workspaces(app, db_session)
    async with auth_client(app, db_session, owner_a) as a_client:
        await a_client.patch(
            "/api/v1/workspaces/me",
            json={"name": "Workspace A — renamed"},
            headers=csrf_headers(a_client),
        )

    # Workspace B's name is unaffected — verify via owner B's view.
    async with auth_client(app, db_session, owner_b) as b_client:
        response = await b_client.get("/api/v1/workspaces/me")
        assert response.status_code == 200
        assert response.json()["name"] == "Workspace B"
