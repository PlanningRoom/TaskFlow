"""Phase C1 — invitation endpoints (PRD §3.3)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.audit_log import AuditLog
from taskflow.db.models.invitation import Invitation
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


async def test_owner_can_send_invitation(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    response = await http.post(
        "/api/v1/workspaces/me/invitations",
        json={"email": "newhire@example.com", "role": "member"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["invitation"]["email"] == "newhire@example.com"
    assert body["invitation"]["role"] == "member"
    assert body["invitation"]["status"] == "pending"

    invitation = await db_session.scalar(
        select(Invitation).where(Invitation.email == "newhire@example.com")
    )
    assert invitation is not None
    assert invitation.token_hash

    audit = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "workspace.invitation.sent")
    )
    assert audit is not None and audit.target_id == invitation.id


async def test_admin_can_send_invitation(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    admin = await make_user(db_session, workspace_id=owner.workspace_id, role="admin")
    async with auth_client(app, db_session, admin) as client:
        response = await client.post(
            "/api/v1/workspaces/me/invitations",
            json={"email": "newhire@example.com", "role": "member"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 200


@pytest.mark.parametrize("role", ["member", "viewer"])
async def test_member_viewer_cannot_invite(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession, role: str
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    other = await make_user(
        db_session, workspace_id=owner.workspace_id, role=role, email=f"{role}@x.com"
    )
    async with auth_client(app, db_session, other) as client:
        response = await client.post(
            "/api/v1/workspaces/me/invitations",
            json={"email": "ignored@example.com", "role": "member"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 403


async def test_duplicate_pending_invitation_conflicts(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    payload = {"email": "newhire@example.com", "role": "member"}
    r1 = await http.post("/api/v1/workspaces/me/invitations", json=payload, headers=headers)
    assert r1.status_code == 200
    r2 = await http.post("/api/v1/workspaces/me/invitations", json=payload, headers=headers)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "INVITATION_PENDING"


async def test_resend_regenerates_token_and_extends_expiry(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    sent = (
        await http.post(
            "/api/v1/workspaces/me/invitations",
            json={"email": "newhire@example.com", "role": "member"},
            headers=headers,
        )
    ).json()
    invitation_id = sent["invitation"]["id"]

    invitation = await db_session.scalar(select(Invitation).where(Invitation.id == invitation_id))
    assert invitation is not None
    original_token = invitation.token_hash
    original_expires = invitation.expires_at

    response = await http.post(
        f"/api/v1/workspaces/me/invitations/{invitation_id}/resend", headers=headers
    )
    assert response.status_code == 200, response.text

    db_session.expire_all()
    refreshed = await db_session.scalar(select(Invitation).where(Invitation.id == invitation_id))
    assert refreshed is not None
    assert refreshed.token_hash != original_token
    assert refreshed.expires_at >= original_expires

    audit = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "workspace.invitation.resent")
    )
    assert audit is not None


async def test_resend_unknown_invitation_404(http: AsyncClient) -> None:
    await signup_owner(http)
    from uuid import uuid4

    response = await http.post(
        f"/api/v1/workspaces/me/invitations/{uuid4()}/resend",
        headers=csrf_headers(http),
    )
    assert response.status_code == 404


async def test_resend_accepted_invitation_conflicts(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    from datetime import UTC, datetime

    await signup_owner(http)
    sent = (
        await http.post(
            "/api/v1/workspaces/me/invitations",
            json={"email": "newhire@example.com", "role": "member"},
            headers=csrf_headers(http),
        )
    ).json()
    invitation_id = sent["invitation"]["id"]

    # Mark accepted directly.
    invitation = await db_session.scalar(select(Invitation).where(Invitation.id == invitation_id))
    assert invitation is not None
    invitation.accepted_at = datetime.now(UTC)
    await db_session.commit()

    response = await http.post(
        f"/api/v1/workspaces/me/invitations/{invitation_id}/resend",
        headers=csrf_headers(http),
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVITATION_ACCEPTED"


async def test_list_invitations(http: AsyncClient) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    await http.post(
        "/api/v1/workspaces/me/invitations",
        json={"email": "a@example.com", "role": "member"},
        headers=headers,
    )
    await http.post(
        "/api/v1/workspaces/me/invitations",
        json={"email": "b@example.com", "role": "admin"},
        headers=headers,
    )
    response = await http.get("/api/v1/workspaces/me/invitations")
    assert response.status_code == 200
    body = response.json()
    assert len(body["invitations"]) == 2


async def test_list_invitations_reports_accepted_and_expired_status(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    import secrets
    from datetime import UTC, datetime, timedelta

    from taskflow.auth.tokens import hash_token

    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    now = datetime.now(UTC)

    db_session.add(
        Invitation(
            workspace_id=owner.workspace_id,
            email="accepted@example.com",
            role="member",
            token_hash=hash_token(secrets.token_urlsafe(32)),
            invited_by=owner.id,
            expires_at=now + timedelta(days=7),
            accepted_at=now - timedelta(hours=1),
        )
    )
    db_session.add(
        Invitation(
            workspace_id=owner.workspace_id,
            email="expired@example.com",
            role="member",
            token_hash=hash_token(secrets.token_urlsafe(32)),
            invited_by=owner.id,
            expires_at=now - timedelta(days=1),
        )
    )
    await db_session.commit()

    response = await http.get("/api/v1/workspaces/me/invitations")
    assert response.status_code == 200
    statuses = {i["email"]: i["status"] for i in response.json()["invitations"]}
    assert statuses["accepted@example.com"] == "accepted"
    assert statuses["expired@example.com"] == "expired"
