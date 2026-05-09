"""Phase C2 — project access endpoints (PRD §5.2)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.audit_log import AuditLog
from taskflow.db.models.project import ProjectMembership
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


async def _make_project(http: AsyncClient, name: str = "Project") -> str:
    body = (
        await http.post("/api/v1/projects", json={"name": name}, headers=csrf_headers(http))
    ).json()
    return str(body["id"])


async def test_grant_and_revoke_access(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(
        db_session, workspace_id=owner.workspace_id, role="member", email="m@x.com"
    )

    project_id = await _make_project(http)

    # Grant
    grant = await http.post(
        f"/api/v1/projects/{project_id}/access",
        json={"user_id": str(member.id)},
        headers=headers,
    )
    assert grant.status_code == 200
    membership = await db_session.scalar(
        select(ProjectMembership).where(ProjectMembership.user_id == member.id)
    )
    assert membership is not None

    audit_added = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "project.access.added")
    )
    assert audit_added is not None

    # List
    listed = await http.get(f"/api/v1/projects/{project_id}/access")
    assert listed.status_code == 200
    assert any(m["user"]["id"] == str(member.id) for m in listed.json()["members"])

    # Revoke
    revoke = await http.delete(f"/api/v1/projects/{project_id}/access/{member.id}", headers=headers)
    assert revoke.status_code == 200

    audit_removed = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "project.access.removed")
    )
    assert audit_removed is not None


async def test_grant_existing_membership_conflicts(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    project_id = await _make_project(http)
    headers = csrf_headers(http)

    r1 = await http.post(
        f"/api/v1/projects/{project_id}/access",
        json={"user_id": str(member.id)},
        headers=headers,
    )
    assert r1.status_code == 200

    r2 = await http.post(
        f"/api/v1/projects/{project_id}/access",
        json={"user_id": str(member.id)},
        headers=headers,
    )
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "PROJECT_ACCESS_EXISTS"


async def test_revoke_nonexistent_membership_404(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    project_id = await _make_project(http)

    response = await http.delete(
        f"/api/v1/projects/{project_id}/access/{member.id}",
        headers=csrf_headers(http),
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PROJECT_ACCESS_NOT_FOUND"


async def test_member_cannot_manage_access(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    target = await make_user(
        db_session, workspace_id=owner.workspace_id, role="member", email="t@x.com"
    )
    project_id = await _make_project(http)

    async with auth_client(app, db_session, member) as client:
        r = await client.post(
            f"/api/v1/projects/{project_id}/access",
            json={"user_id": str(target.id)},
            headers=csrf_headers(client),
        )
        assert r.status_code == 403


async def test_grant_unknown_user_404(
    http: AsyncClient,
) -> None:
    await signup_owner(http)
    project_id = await _make_project(http)
    from uuid import uuid4

    response = await http.post(
        f"/api/v1/projects/{project_id}/access",
        json={"user_id": str(uuid4())},
        headers=csrf_headers(http),
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"
