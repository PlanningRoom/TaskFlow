"""Phase C2 — project CRUD endpoints (PRD §5)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.audit_log import AuditLog
from taskflow.db.models.project import Project, ProjectMembership
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


async def test_owner_can_create_project(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    response = await http.post(
        "/api/v1/projects",
        json={"name": "Aurora Web", "description": "the website", "color": "indigo"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["name"] == "Aurora Web"
    assert body["color"] == "indigo"

    project = await db_session.scalar(select(Project).where(Project.name == "Aurora Web"))
    assert project is not None

    audit = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "project.created")
    )
    assert audit is not None and audit.target_id == project.id


async def test_member_create_project_grants_self_access(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    async with auth_client(app, db_session, member) as client:
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Member Project"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 200
        body = response.json()
        project_id = body["id"]

    membership = await db_session.scalar(
        select(ProjectMembership).where(
            ProjectMembership.project_id == project_id,
            ProjectMembership.user_id == member.id,
        )
    )
    assert membership is not None


async def test_viewer_cannot_create_project(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    viewer = await make_user(
        db_session, workspace_id=owner.workspace_id, role="viewer", email="v@x.com"
    )
    async with auth_client(app, db_session, viewer) as client:
        response = await client.post(
            "/api/v1/projects",
            json={"name": "Forbidden"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 403


async def test_owner_admin_see_all_projects(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    await http.post("/api/v1/projects", json={"name": "Project A"}, headers=headers)
    await http.post("/api/v1/projects", json={"name": "Project B"}, headers=headers)

    response = await http.get("/api/v1/projects")
    assert response.status_code == 200
    assert len(response.json()["projects"]) == 2


async def test_member_only_sees_projects_with_access(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    # Owner makes project A; doesn't grant member access.
    a = (await http.post("/api/v1/projects", json={"name": "A"}, headers=headers)).json()
    _ = a

    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")

    async with auth_client(app, db_session, member) as client:
        # Member sees zero projects (no access to Owner's A).
        r = await client.get("/api/v1/projects")
        assert r.status_code == 200
        assert r.json()["projects"] == []

        # Member creates B; sees only B.
        b = (
            await client.post("/api/v1/projects", json={"name": "B"}, headers=csrf_headers(client))
        ).json()
        r2 = await client.get("/api/v1/projects")
        assert [p["name"] for p in r2.json()["projects"]] == ["B"]
        assert b["id"] in {p["id"] for p in r2.json()["projects"]}


async def test_get_project_404_when_missing(http: AsyncClient) -> None:
    await signup_owner(http)
    from uuid import uuid4

    response = await http.get(f"/api/v1/projects/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PROJECT_NOT_FOUND"


async def test_member_without_access_cannot_get_project(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project = (
        await http.post(
            "/api/v1/projects",
            json={"name": "Locked"},
            headers=csrf_headers(http),
        )
    ).json()
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    async with auth_client(app, db_session, member) as client:
        response = await client.get(f"/api/v1/projects/{project['id']}")
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "PROJECT_ACCESS_DENIED"


async def test_admin_can_update_project(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    project = (
        await http.post("/api/v1/projects", json={"name": "Original"}, headers=headers)
    ).json()

    response = await http.patch(
        f"/api/v1/projects/{project['id']}",
        json={"name": "Renamed", "color": "amber"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"
    assert response.json()["color"] == "amber"

    audit = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "project.updated")
    )
    assert audit is not None


async def test_member_cannot_update_project(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    project = (
        await http.post("/api/v1/projects", json={"name": "Locked"}, headers=csrf_headers(http))
    ).json()

    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    async with auth_client(app, db_session, member) as client:
        response = await client.patch(
            f"/api/v1/projects/{project['id']}",
            json={"name": "hijack"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 403
