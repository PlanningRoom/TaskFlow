"""Phase B4 — auth endpoint integration tests (TDD §11, PRD §3, §20)."""

from __future__ import annotations

import secrets
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.tokens import hash_token
from taskflow.db.models.audit_log import AuditLog
from taskflow.db.models.invitation import Invitation
from taskflow.db.models.password_reset_token import PasswordResetToken
from taskflow.db.models.session import Session as SessionModel
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace
from taskflow.db.uuid7 import uuid7
from taskflow.settings import settings

pytestmark = pytest.mark.asyncio


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
async def app(db_engine: None) -> FastAPI:
    # `cookie_secure=False` so the TestClient (HTTP) keeps the cookie.
    settings.cookie_secure = False
    from taskflow.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
async def http(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


SIGNUP_PAYLOAD = {
    "email": "owner@example.com",
    "password": "correct-horse-battery-staple",
    "display_name": "Aurora Owner",
    "workspace_name": "Aurora Studio",
}


def _csrf_headers(client: AsyncClient) -> dict[str, str]:
    csrf = client.cookies.get(settings.csrf_cookie_name)
    assert csrf is not None
    return {settings.csrf_header_name: csrf}


# ──────────────────────────────────────────────────────────────────────────────
# Sign-up
# ──────────────────────────────────────────────────────────────────────────────


async def test_signup_creates_workspace_and_owner_and_sets_cookies(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    response = await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user"]["email"] == SIGNUP_PAYLOAD["email"]
    assert body["user"]["role"] == "owner"
    assert body["user"]["initials"] == "AO"  # "Aurora Owner"
    assert body["user"]["avatar_color"]

    # Cookies set with the right attributes (TDD §11.1).
    set_cookie = response.headers.get_list("set-cookie")
    session_cookies = [c for c in set_cookie if c.startswith("taskflow_session")]
    csrf_cookies = [c for c in set_cookie if c.startswith("csrf_token")]
    assert session_cookies and csrf_cookies
    assert all("HttpOnly" in c for c in session_cookies)
    assert all("HttpOnly" not in c for c in csrf_cookies)  # JS-readable per ADR 051
    assert all("samesite=lax" in c.lower() for c in set_cookie)
    # 30-day absolute lifetime (TDD §11.1).
    expected_max_age = "Max-Age=" + str(30 * 86400)
    assert all(expected_max_age in c for c in set_cookie)

    # DB rows created.
    user = await db_session.scalar(select(User).where(User.email.ilike(SIGNUP_PAYLOAD["email"])))
    assert user is not None and user.role == "owner"
    workspace = await db_session.scalar(select(Workspace).where(Workspace.id == user.workspace_id))
    assert workspace is not None and workspace.name == SIGNUP_PAYLOAD["workspace_name"]
    audit = (
        await db_session.execute(select(AuditLog).where(AuditLog.event_type == "auth.signup"))
    ).scalar_one_or_none()
    assert audit is not None and audit.actor_id == user.id


async def test_signup_rejects_duplicate_email(http: AsyncClient) -> None:
    r1 = await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert r1.status_code == 200
    # New transport / client to drop cookies (so it's an honest second signup).
    async with AsyncClient(
        transport=ASGITransport(app=(await http_app(http))), base_url="http://testserver"
    ) as fresh:
        r2 = await fresh.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "EMAIL_TAKEN"


async def http_app(client: AsyncClient) -> FastAPI:
    transport = client._transport
    assert isinstance(transport, ASGITransport)
    return transport.app  # type: ignore[return-value]


async def test_signup_rejects_invalid_password(http: AsyncClient) -> None:
    payload = SIGNUP_PAYLOAD | {"password": "short"}
    response = await http.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ──────────────────────────────────────────────────────────────────────────────
# Login / logout / me
# ──────────────────────────────────────────────────────────────────────────────


async def test_login_after_signup_succeeds(http: AsyncClient) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    http.cookies.clear()
    response = await http.post(
        "/api/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]},
    )
    assert response.status_code == 200, response.text
    assert http.cookies.get(settings.session_cookie_name) is not None
    assert http.cookies.get(settings.csrf_cookie_name) is not None


async def test_login_with_wrong_password_returns_401(http: AsyncClient) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    http.cookies.clear()
    response = await http.post(
        "/api/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": "nope"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_me_returns_current_user(http: AsyncClient) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = await http.get("/api/v1/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == SIGNUP_PAYLOAD["email"]
    assert body["role"] == "owner"


async def test_me_requires_session(http: AsyncClient) -> None:
    response = await http.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


async def test_logout_requires_csrf(http: AsyncClient) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    # Without the CSRF header — should fail.
    bad = await http.post("/api/v1/auth/logout")
    assert bad.status_code == 403
    assert bad.json()["error"]["code"] == "CSRF_INVALID"

    # With it — should succeed.
    good = await http.post("/api/v1/auth/logout", headers=_csrf_headers(http))
    assert good.status_code == 200
    # Cookies cleared / session row deleted.
    cookie_val = http.cookies.get(settings.session_cookie_name) or ""
    assert "taskflow_session=" not in cookie_val


# ──────────────────────────────────────────────────────────────────────────────
# Password reset
# ──────────────────────────────────────────────────────────────────────────────


async def test_password_reset_request_is_no_enumeration(http: AsyncClient) -> None:
    # Unknown email → still 200.
    r = await http.post("/api/v1/auth/password-reset/request", json={"email": "nobody@example.com"})
    assert r.status_code == 200
    assert r.json() == {"ok": True}


async def test_password_reset_confirm_revokes_other_sessions(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    user = await db_session.scalar(select(User).where(User.email.ilike(SIGNUP_PAYLOAD["email"])))
    assert user is not None

    # Issue a reset token directly (the email path is wired in D2).
    raw = secrets.token_urlsafe(32)
    db_session.add(
        PasswordResetToken(
            token_hash=hash_token(raw),
            user_id=user.id,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
    )
    await db_session.commit()

    response = await http.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": raw, "new_password": "new-correct-horse-battery"},
    )
    assert response.status_code == 200

    # All sessions for the user have been deleted.
    remaining = (
        await db_session.execute(select(SessionModel).where(SessionModel.user_id == user.id))
    ).all()
    assert remaining == []


async def test_password_reset_confirm_rejects_invalid_token(http: AsyncClient) -> None:
    response = await http.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": "not-a-real-token-but-long-enough", "new_password": "abc12345"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_TOKEN"


# ──────────────────────────────────────────────────────────────────────────────
# Profile updates
# ──────────────────────────────────────────────────────────────────────────────


async def test_patch_me_updates_display_name(http: AsyncClient) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = await http.patch(
        "/api/v1/auth/me",
        json={"display_name": "Aurora Boss"},
        headers=_csrf_headers(http),
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Aurora Boss"


async def test_change_password_revokes_other_sessions_keeps_current(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    # Sign up: session 1.
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    # Second login from a "different browser" — session 2.
    async with AsyncClient(
        transport=ASGITransport(app=(await http_app(http))), base_url="http://testserver"
    ) as other:
        await other.post(
            "/api/v1/auth/login",
            json={"email": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]},
        )
        user = await db_session.scalar(
            select(User).where(User.email.ilike(SIGNUP_PAYLOAD["email"]))
        )
        assert user is not None
        sessions_before = (
            await db_session.execute(select(SessionModel).where(SessionModel.user_id == user.id))
        ).all()
        assert len(sessions_before) == 2

    # Change password from the original client.
    response = await http.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": SIGNUP_PAYLOAD["password"],
            "new_password": "another-correct-horse",
        },
        headers=_csrf_headers(http),
    )
    assert response.status_code == 200

    sessions_after = (
        await db_session.execute(select(SessionModel).where(SessionModel.user_id == user.id))
    ).all()
    assert len(sessions_after) == 1  # only the current session survives
    # Original client still works.
    me = await http.get("/api/v1/auth/me")
    assert me.status_code == 200


async def test_self_delete_anonymizes_and_unassigns(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    user = await db_session.scalar(select(User).where(User.email.ilike(SIGNUP_PAYLOAD["email"])))
    assert user is not None

    response = await http.request(
        "DELETE",
        "/api/v1/auth/me",
        json={"password": SIGNUP_PAYLOAD["password"]},
        headers=_csrf_headers(http),
    )
    assert response.status_code == 200, response.text

    # Cross-session mutation; bypass identity-map cache by re-fetching with populate_existing.
    refreshed = await db_session.get(User, user.id, populate_existing=True)
    assert refreshed is not None
    assert refreshed.email is None
    assert refreshed.name is None
    assert refreshed.password_hash is None
    assert refreshed.deleted_at is not None


# ──────────────────────────────────────────────────────────────────────────────
# Invitation acceptance
# ──────────────────────────────────────────────────────────────────────────────


async def test_accept_invitation_for_new_user(http: AsyncClient, db_session: AsyncSession) -> None:
    # Bootstrap a workspace + owner.
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    owner = await db_session.scalar(select(User).where(User.email.ilike(SIGNUP_PAYLOAD["email"])))
    assert owner is not None

    raw = secrets.token_urlsafe(32)
    invitation = Invitation(
        workspace_id=owner.workspace_id,
        email="newhire@example.com",
        role="member",
        token_hash=hash_token(raw),
        invited_by=owner.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    db_session.add(invitation)
    await db_session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=(await http_app(http))), base_url="http://testserver"
    ) as fresh:
        response = await fresh.post(
            "/api/v1/auth/accept-invitation",
            json={
                "token": raw,
                "password": "another-correct-horse",
                "display_name": "New Hire",
            },
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user"]["email"] == "newhire@example.com"
    assert body["user"]["role"] == "member"

    invited = await db_session.scalar(select(User).where(User.email.ilike("newhire@example.com")))
    assert invited is not None and invited.workspace_id == owner.workspace_id


async def test_accept_invitation_rejects_expired(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    owner = await db_session.scalar(select(User).where(User.email.ilike(SIGNUP_PAYLOAD["email"])))
    assert owner is not None

    raw = secrets.token_urlsafe(32)
    db_session.add(
        Invitation(
            workspace_id=owner.workspace_id,
            email="too-late@example.com",
            role="member",
            token_hash=hash_token(raw),
            invited_by=owner.id,
            expires_at=datetime.now(UTC) - timedelta(seconds=1),
        )
    )
    await db_session.commit()

    response = await http.post(
        "/api/v1/auth/accept-invitation",
        json={"token": raw, "password": "ignore-me", "display_name": "Too Late"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVITATION_EXPIRED"


async def test_accept_invitation_rejects_invalid_token(http: AsyncClient) -> None:
    response = await http.post(
        "/api/v1/auth/accept-invitation",
        json={
            "token": "definitely-not-real-but-long-enough",
            "password": "12345678",
            "display_name": "X",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_TOKEN"


async def test_accept_invitation_new_user_requires_account_fields(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    owner = await db_session.scalar(select(User).where(User.email.ilike(SIGNUP_PAYLOAD["email"])))
    assert owner is not None

    raw = secrets.token_urlsafe(32)
    db_session.add(
        Invitation(
            workspace_id=owner.workspace_id,
            email="fields-required@example.com",
            role="member",
            token_hash=hash_token(raw),
            invited_by=owner.id,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
    )
    await db_session.commit()

    # New email but no password/display_name → service rejects.
    response = await http.post("/api/v1/auth/accept-invitation", json={"token": raw})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ACCOUNT_FIELDS_REQUIRED"


async def test_accept_invitation_existing_user_moves_workspace(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    # Owner A's workspace (the inviter).
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    owner = await db_session.scalar(select(User).where(User.email.ilike(SIGNUP_PAYLOAD["email"])))
    assert owner is not None

    # A pre-existing live user (currently owner of their own workspace B).
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as other:
        await other.post(
            "/api/v1/auth/signup",
            json={
                "email": "existing@example.com",
                "password": "correct-horse-battery-staple-2",
                "display_name": "Existing User",
                "workspace_name": "Workspace B",
            },
        )
    existing = await db_session.scalar(select(User).where(User.email.ilike("existing@example.com")))
    assert existing is not None
    original_ws = existing.workspace_id

    # Owner A invites that existing email.
    raw = secrets.token_urlsafe(32)
    db_session.add(
        Invitation(
            workspace_id=owner.workspace_id,
            email="existing@example.com",
            role="member",
            token_hash=hash_token(raw),
            invited_by=owner.id,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
    )
    await db_session.commit()

    # Accept — no password/display_name needed for an existing account.
    response = await http.post("/api/v1/auth/accept-invitation", json={"token": raw})
    assert response.status_code == 200, response.text
    assert response.json()["user"]["email"] == "existing@example.com"

    moved = await db_session.get(User, existing.id, populate_existing=True)
    assert moved is not None
    assert moved.workspace_id == owner.workspace_id != original_ws
    assert moved.role == "member"


# ──────────────────────────────────────────────────────────────────────────────
# Authenticated mutations — wrong-credential branches
# ──────────────────────────────────────────────────────────────────────────────


async def test_change_password_wrong_current_returns_401(http: AsyncClient) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = await http.post(
        "/api/v1/auth/change-password",
        json={"current_password": "not-the-password", "new_password": "another-correct-horse"},
        headers=_csrf_headers(http),
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_delete_account_wrong_password_returns_401(http: AsyncClient) -> None:
    await http.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = await http.request(
        "DELETE",
        "/api/v1/auth/me",
        json={"password": "not-the-password"},
        headers=_csrf_headers(http),
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


# ──────────────────────────────────────────────────────────────────────────────
# Direct service-layer calls — branches not reachable through the HTTP path
# (FastAPI always supplies a Request; the endpoints never pass request=None).
# ──────────────────────────────────────────────────────────────────────────────


async def test_login_service_tolerates_no_request(db_session: AsyncSession) -> None:
    from taskflow.services import auth as auth_service

    await auth_service.signup(
        db_session,
        email="norq@example.com",
        password="correct-horse-battery-staple",
        display_name="No Request",
        workspace_name="NoReq WS",
    )
    await db_session.commit()

    # request=None exercises the _client_ip / _user_agent None-guards.
    user, tokens = await auth_service.login(
        db_session, email="norq@example.com", password="correct-horse-battery-staple"
    )
    assert user.email == "norq@example.com"
    assert tokens.session_token


async def test_confirm_password_reset_rejects_deleted_user(db_session: AsyncSession) -> None:
    from taskflow.services import auth as auth_service
    from taskflow.services.users import anonymize_user

    user, _ = await auth_service.signup(
        db_session,
        email="willdelete@example.com",
        password="correct-horse-battery-staple",
        display_name="Will Delete",
        workspace_name="Delete WS",
    )
    await db_session.commit()

    _, raw = await auth_service.request_password_reset(db_session, email="willdelete@example.com")
    await db_session.commit()
    assert raw is not None

    # User is anonymized after the token was issued → confirm must reject.
    await anonymize_user(db_session, user)
    await db_session.commit()

    with pytest.raises(auth_service.InvalidTokenError):
        await auth_service.confirm_password_reset(
            db_session, raw_token=raw, new_password="brand-new-correct-horse"
        )


# ──────────────────────────────────────────────────────────────────────────────
# UUIDv7 sanity
# ──────────────────────────────────────────────────────────────────────────────


async def test_uuid7_versions_increase_in_time_order() -> None:
    a = uuid7()
    b = uuid7()
    # Time-ordered: the high 48 bits encode unix-ms; b ≥ a as integers.
    assert b.int >= a.int
    assert a.version == 7 and b.version == 7
