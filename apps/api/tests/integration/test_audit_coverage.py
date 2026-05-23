"""Audit-log coverage sweep (Phase E1 / ADR 084).

Drives every flow that should write an `audit_log` row, then asserts that the
distinct set of `event_type` values written matches `AUDIT_EVENT_TYPES` exactly.
A failure here means either:

- A service path stopped emitting an event it used to (regression), or
- A new event was added to `AUDIT_EVENT_TYPES` without a corresponding emission.

The test is intentionally one big walkthrough rather than 22 separate cases:
the assertion is "every documented event was observed", which is naturally a
set-equality check at the end.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.audit_log import AUDIT_EVENT_TYPES, AuditLog
from taskflow.db.models.invitation import Invitation
from taskflow.db.models.user import User
from taskflow.settings import settings
from tests.integration._helpers import csrf_headers, make_user, signup_owner

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


@pytest.fixture
def captured_tokens(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Capture raw password-reset and invitation tokens that the endpoints
    would otherwise only deliver by email."""
    bag: dict[str, str] = {}

    from taskflow.api.v1 import auth as auth_routes
    from taskflow.api.v1 import workspaces as workspace_routes

    def _cap_reset(email: str, raw_token: str) -> None:
        bag["password_reset"] = raw_token

    def _cap_invite(email: str, raw_token: str) -> None:
        bag.setdefault("invitation", raw_token)

    monkeypatch.setattr(auth_routes, "_dispatch_password_reset_email", _cap_reset)
    monkeypatch.setattr(workspace_routes, "_dispatch_invitation_email", _cap_invite)
    return bag


async def test_every_audit_event_is_emitted_by_some_flow(
    app: FastAPI,
    http: AsyncClient,
    db_session: AsyncSession,
    captured_tokens: dict[str, str],
) -> None:
    initial_pw = "correct-horse-battery-staple"
    reset_pw = "reset-horse-correct-staple"
    final_pw = "third-horse-correct-staple"

    # 1) signup -> auth.signup
    await signup_owner(http)

    # 2) logout -> auth.logout
    r = await http.post("/api/v1/auth/logout", headers=csrf_headers(http))
    assert r.status_code == 200, r.text

    # 3) login wrong password -> auth.login.failure
    r = await http.post(
        "/api/v1/auth/login", json={"email": "owner@example.com", "password": "wrong-pw"}
    )
    assert r.status_code == 401

    # 4) login correct -> auth.login.success
    r = await http.post(
        "/api/v1/auth/login", json={"email": "owner@example.com", "password": initial_pw}
    )
    assert r.status_code == 200

    # 5) password reset request -> auth.password_reset.requested
    r = await http.post("/api/v1/auth/password-reset/request", json={"email": "owner@example.com"})
    assert r.status_code == 200
    assert "password_reset" in captured_tokens

    # 6) password reset confirm -> auth.password_reset.completed (revokes sessions)
    r = await http.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": captured_tokens["password_reset"], "new_password": reset_pw},
    )
    assert r.status_code == 200

    # Log back in (reset revoked the session).
    http.cookies.clear()
    r = await http.post(
        "/api/v1/auth/login", json={"email": "owner@example.com", "password": reset_pw}
    )
    assert r.status_code == 200

    # 7) PATCH /auth/me -> auth.profile.updated
    r = await http.patch(
        "/api/v1/auth/me",
        json={"display_name": "Aurora Owner II"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # 8) change-password -> auth.password_changed
    r = await http.post(
        "/api/v1/auth/change-password",
        json={"current_password": reset_pw, "new_password": final_pw},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # 9) PATCH /workspaces/me -> workspace.updated
    r = await http.patch(
        "/api/v1/workspaces/me",
        json={"name": "Aurora Studio Renamed"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # 10) POST /labels -> workspace.label.created
    r = await http.post(
        "/api/v1/labels",
        json={"name": "Audit Sweep", "color": "blue"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text
    label_id = r.json()["id"]

    # 11) PATCH /labels/:id -> workspace.label.updated
    r = await http.patch(
        f"/api/v1/labels/{label_id}",
        json={"name": "Audit Sweep Renamed"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # 12) DELETE /labels/:id -> workspace.label.deleted
    r = await http.delete(f"/api/v1/labels/{label_id}", headers=csrf_headers(http))
    assert r.status_code == 200, r.text

    # 13) POST /projects -> project.created
    r = await http.post(
        "/api/v1/projects",
        json={"name": "Audit Project"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text
    project_id = r.json()["id"]

    # 14) PATCH /projects/:id -> project.updated
    r = await http.patch(
        f"/api/v1/projects/{project_id}",
        json={"description": "audit sweep run"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # Need a Member-or-Viewer user to exercise role-change and project-access
    # (Owner/Admin have implicit access so granting/revoking is meaningless).
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    viewer = await make_user(
        db_session,
        workspace_id=owner.workspace_id,
        role="viewer",
        email="viewer@example.com",
        name="Viewer User",
    )

    # 15) PATCH /workspaces/me/members/:id -> workspace.user.role_changed
    r = await http.patch(
        f"/api/v1/workspaces/me/members/{viewer.id}",
        json={"role": "member"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # Change them back to viewer so project-access has meaning (members of the
    # workspace start with no implicit project access).
    r = await http.patch(
        f"/api/v1/workspaces/me/members/{viewer.id}",
        json={"role": "viewer"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # 16) POST /projects/:id/access -> project.access.added
    r = await http.post(
        f"/api/v1/projects/{project_id}/access",
        json={"user_id": str(viewer.id)},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # 17) DELETE /projects/:id/access/:userId -> project.access.removed
    r = await http.delete(
        f"/api/v1/projects/{project_id}/access/{viewer.id}",
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # 18) POST /workspaces/me/invitations -> workspace.invitation.sent
    r = await http.post(
        "/api/v1/workspaces/me/invitations",
        json={"email": "invitee@example.com", "role": "member"},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text
    invitation_id = r.json()["invitation"]["id"]

    # 19) POST /workspaces/me/invitations/:id/resend -> workspace.invitation.resent
    r = await http.post(
        f"/api/v1/workspaces/me/invitations/{invitation_id}/resend",
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # 20) POST /auth/accept-invitation -> workspace.invitation.accepted
    # Use a fresh client so we're not authenticated as the owner.
    assert "invitation" in captured_tokens
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as guest:
        r = await guest.post(
            "/api/v1/auth/accept-invitation",
            json={
                "token": captured_tokens["invitation"],
                "password": "invitee-horse-correct-staple",
                "display_name": "Invitee User",
            },
        )
        assert r.status_code == 200, r.text

    # 21) DELETE /workspaces/me/members/:viewerId -> workspace.user.removed
    r = await http.delete(
        f"/api/v1/workspaces/me/members/{viewer.id}",
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # 22) DELETE /auth/me -> account.deleted (must be last; owner self-deletes)
    r = await http.request(
        "DELETE",
        "/api/v1/auth/me",
        json={"password": final_pw},
        headers=csrf_headers(http),
    )
    assert r.status_code == 200, r.text

    # ── Assertion ────────────────────────────────────────────────────────────
    rows = await db_session.execute(select(AuditLog.event_type).distinct())
    observed: set[Any] = {row[0] for row in rows.all()}
    expected = set(AUDIT_EVENT_TYPES)
    missing = expected - observed
    unexpected = observed - expected
    assert not missing, f"audit events not emitted by any tested flow: {sorted(missing)}"
    assert not unexpected, f"audit log contains undocumented event types: {sorted(unexpected)}"


async def test_audit_event_types_align_with_check_constraint(db_session: AsyncSession) -> None:
    """The CHECK constraint and the Python tuple must agree.

    Cheap static guard: if someone adds an event type to one side of the model
    file but not the other, this fails immediately.
    """
    from taskflow.db.models.audit_log import _EVENT_TYPE_CHECK_SQL, AUDIT_EVENT_TYPES

    for event in AUDIT_EVENT_TYPES:
        assert f"'{event}'" in _EVENT_TYPE_CHECK_SQL, f"{event} missing from CHECK"
    _ = Invitation  # keep import for future expansion / linter
