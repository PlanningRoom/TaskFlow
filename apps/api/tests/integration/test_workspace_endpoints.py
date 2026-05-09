"""Phase C1 — workspace settings endpoints (PRD §4.1)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.audit_log import AuditLog
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace
from taskflow.settings import settings
from tests.integration._helpers import (
    OWNER_PAYLOAD,
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


async def test_get_workspace_returns_owner_workspace(http: AsyncClient) -> None:
    await signup_owner(http)
    response = await http.get("/api/v1/workspaces/me")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == OWNER_PAYLOAD["workspace_name"]
    assert "id" in body and "created_at" in body


async def test_patch_workspace_updates_name_owner(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    response = await http.patch(
        "/api/v1/workspaces/me",
        json={"name": "New Studio Name"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "New Studio Name"

    workspace = await db_session.scalar(select(Workspace))
    assert workspace is not None and workspace.name == "New Studio Name"

    audit = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "workspace.updated")
    )
    assert audit is not None and audit.target_id == workspace.id


async def test_patch_workspace_admin_allowed(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    admin = await make_user(db_session, workspace_id=owner.workspace_id, role="admin")
    async with auth_client(app, db_session, admin) as client:
        response = await client.patch(
            "/api/v1/workspaces/me",
            json={"name": "Admin Renamed"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 200


@pytest.mark.parametrize("role", ["member", "viewer"])
async def test_patch_workspace_member_viewer_denied(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession, role: str
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    other = await make_user(
        db_session, workspace_id=owner.workspace_id, role=role, email=f"{role}@example.com"
    )
    async with auth_client(app, db_session, other) as client:
        response = await client.patch(
            "/api/v1/workspaces/me",
            json={"name": "Should Fail"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "PERMISSION_DENIED"


async def test_patch_workspace_requires_csrf(http: AsyncClient) -> None:
    await signup_owner(http)
    response = await http.patch("/api/v1/workspaces/me", json={"name": "No CSRF"})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "CSRF_INVALID"


async def test_get_workspace_unauthenticated(http: AsyncClient) -> None:
    response = await http.get("/api/v1/workspaces/me")
    assert response.status_code == 401
