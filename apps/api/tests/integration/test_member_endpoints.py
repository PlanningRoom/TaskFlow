"""Phase C1 — member endpoints (PRD §4.2, ADR 065)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.audit_log import AuditLog
from taskflow.db.models.session import Session as SessionModel
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


async def test_list_members_owner_sees_all(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    await make_user(db_session, workspace_id=owner.workspace_id, role="member", name="Mable")
    await make_user(db_session, workspace_id=owner.workspace_id, role="viewer", name="Vince")

    response = await http.get("/api/v1/workspaces/me/members")
    assert response.status_code == 200
    body = response.json()
    assert len(body["members"]) == 3
    roles = sorted(m["role"] for m in body["members"])
    assert roles == ["member", "owner", "viewer"]


@pytest.mark.parametrize("role", ["member", "viewer"])
async def test_list_members_member_viewer_denied(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession, role: str
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    other = await make_user(
        db_session, workspace_id=owner.workspace_id, role=role, email=f"{role}@x.com"
    )
    async with auth_client(app, db_session, other) as client:
        response = await client.get("/api/v1/workspaces/me/members")
        assert response.status_code == 403


async def test_owner_can_change_member_role(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")

    response = await http.patch(
        f"/api/v1/workspaces/me/members/{member.id}",
        json={"role": "admin"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text
    assert response.json()["role"] == "admin"

    audit = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "workspace.user.role_changed")
    )
    assert audit is not None
    assert audit.metadata_["from"] == "member"
    assert audit.metadata_["to"] == "admin"


async def test_owner_cannot_change_own_role(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    response = await http.patch(
        f"/api/v1/workspaces/me/members/{owner.id}",
        json={"role": "admin"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SELF_ROLE_CHANGE_FORBIDDEN"


async def test_member_cannot_change_role(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    target = await make_user(
        db_session, workspace_id=owner.workspace_id, role="viewer", name="Target"
    )
    async with auth_client(app, db_session, member) as client:
        response = await client.patch(
            f"/api/v1/workspaces/me/members/{target.id}",
            json={"role": "member"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 403


async def test_owner_can_remove_member_anonymizes(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    target = await make_user(
        db_session, workspace_id=owner.workspace_id, role="member", name="Removable"
    )
    target_id = target.id

    response = await http.delete(
        f"/api/v1/workspaces/me/members/{target_id}",
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text

    db_session.expire_all()
    refreshed = await db_session.scalar(select(User).where(User.id == target_id))
    assert refreshed is not None
    assert refreshed.deleted_at is not None
    assert refreshed.email is None
    assert refreshed.name is None
    assert refreshed.password_hash is None

    sessions = await db_session.scalars(
        select(SessionModel).where(SessionModel.user_id == target_id)
    )
    assert sessions.first() is None


async def test_admin_cannot_remove_member(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    admin = await make_user(db_session, workspace_id=owner.workspace_id, role="admin")
    target = await make_user(
        db_session, workspace_id=owner.workspace_id, role="member", name="Target"
    )
    async with auth_client(app, db_session, admin) as client:
        response = await client.delete(
            f"/api/v1/workspaces/me/members/{target.id}",
            headers=csrf_headers(client),
        )
        assert response.status_code == 403


async def test_owner_cannot_remove_self(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    response = await http.delete(
        f"/api/v1/workspaces/me/members/{owner.id}",
        headers=csrf_headers(http),
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SELF_REMOVE_FORBIDDEN"


async def test_remove_unknown_member_404(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    from uuid import uuid4

    response = await http.delete(
        f"/api/v1/workspaces/me/members/{uuid4()}",
        headers=csrf_headers(http),
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "MEMBER_NOT_FOUND"


async def test_remove_member_is_idempotent(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    target = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    headers = csrf_headers(http)

    first = await http.delete(f"/api/v1/workspaces/me/members/{target.id}", headers=headers)
    assert first.status_code == 200, first.text
    # Removing an already-anonymized member is a no-op (no second audit row).
    second = await http.delete(f"/api/v1/workspaces/me/members/{target.id}", headers=headers)
    assert second.status_code == 200, second.text

    audit_rows = (
        await db_session.execute(
            select(AuditLog).where(AuditLog.event_type == "workspace.user.removed")
        )
    ).all()
    assert len(audit_rows) == 1


async def test_change_role_on_removed_member_404(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    target = await make_user(db_session, workspace_id=owner.workspace_id, role="member")
    headers = csrf_headers(http)

    await http.delete(f"/api/v1/workspaces/me/members/{target.id}", headers=headers)
    # The anonymized user is no longer a role-change target.
    response = await http.patch(
        f"/api/v1/workspaces/me/members/{target.id}",
        json={"role": "admin"},
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "MEMBER_NOT_FOUND"
