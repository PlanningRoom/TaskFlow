"""Rate-limit integration tests (Phase E1 / ADR 052).

Each test re-enables the slowapi limiter (the global conftest disables it for
the rest of the suite) and points the relevant limit at a very small value so
the test can exhaust it cheaply, then asserts the next call returns the
ADR 043 RATE_LIMITED envelope with a Retry-After header.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.rate_limit import limiter
from taskflow.settings import settings
from tests.integration._helpers import csrf_headers, signup_owner

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
def enable_limiter() -> None:
    """Re-enable the limiter for this test (autouse fixture disables it globally)."""
    limiter.reset()
    limiter.enabled = True


def _assert_rate_limited(response: object) -> None:
    """ADR 043 envelope + Retry-After header sanity."""
    # httpx.Response — typed loosely so this helper stays simple.
    assert response.status_code == 429, getattr(response, "text", response)  # type: ignore[attr-defined]
    body = response.json()  # type: ignore[attr-defined]
    assert body["error"]["code"] == "RATE_LIMITED", body
    assert response.headers.get("Retry-After") is not None  # type: ignore[attr-defined]


async def test_signup_per_ip_limit_trips(
    enable_limiter: None,
    monkeypatch: pytest.MonkeyPatch,
    app: FastAPI,
) -> None:
    """3rd-party signups from the same IP get bounced after the IP limit."""
    monkeypatch.setattr(settings, "rate_limit_signup_per_ip", "2/minute")
    # Reload the decorator's bound limit string by re-decorating? slowapi reads
    # the limit string from the decorator call at import time. To make this
    # test isolated without re-importing, we instead exhaust the configured
    # default (3/hour) — that's only 3 requests and the test client is fast.
    monkeypatch.setattr(settings, "rate_limit_signup_per_ip", "3/hour")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 3 signups should succeed-or-conflict (we don't care which; only that
        # the limiter doesn't reject them). Use distinct emails so signup
        # itself succeeds and we exercise the limiter not the dedupe path.
        for i in range(3):
            await client.post(
                "/api/v1/auth/signup",
                json={
                    "email": f"user{i}@example.com",
                    "password": "correct-horse-battery-staple",
                    "display_name": f"User {i}",
                    "workspace_name": f"WS {i}",
                },
            )
        # 4th must be rate limited.
        r = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user4@example.com",
                "password": "correct-horse-battery-staple",
                "display_name": "User 4",
                "workspace_name": "WS 4",
            },
        )
        _assert_rate_limited(r)


async def test_login_per_ip_limit_trips_regardless_of_email(
    enable_limiter: None,
    http: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Per-IP login limit trips even when attempts use different emails."""
    await signup_owner(http)
    # logout to clear the post-signup session.
    await http.post("/api/v1/auth/logout", headers=csrf_headers(http))
    http.cookies.clear()

    # 5 failures from the same IP with rotating emails to avoid hitting the
    # per-email cap; then the 6th must be 429.
    for i in range(5):
        r = await http.post(
            "/api/v1/auth/login",
            json={"email": f"unknown{i}@example.com", "password": "nope"},
        )
        assert r.status_code in {401, 200}
    r = await http.post(
        "/api/v1/auth/login",
        json={"email": "another@example.com", "password": "nope"},
    )
    _assert_rate_limited(r)


async def test_login_per_email_limit_trips_across_ips(
    enable_limiter: None,
    app: FastAPI,
    http: AsyncClient,
) -> None:
    """Per-email login limit trips even when attempts come from rotated IPs."""
    await signup_owner(http)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 10 failures spread across 10 different X-Forwarded-For values; 11th trips.
        for i in range(10):
            r = await client.post(
                "/api/v1/auth/login",
                json={"email": "owner@example.com", "password": "nope"},
                headers={"X-Forwarded-For": f"203.0.113.{i + 1}"},
            )
            assert r.status_code in {401, 200, 429}, r.text
        r = await client.post(
            "/api/v1/auth/login",
            json={"email": "owner@example.com", "password": "nope"},
            headers={"X-Forwarded-For": "203.0.113.250"},
        )
        _assert_rate_limited(r)


async def test_password_reset_request_per_ip_limit_trips(
    enable_limiter: None,
    http: AsyncClient,
) -> None:
    """3rd password-reset request from the same IP gets bounced (default 3/hour)."""
    await signup_owner(http)
    for _ in range(3):
        r = await http.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "someone@example.com"},
        )
        assert r.status_code == 200
    r = await http.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "another@example.com"},
    )
    _assert_rate_limited(r)


async def test_invitations_per_workspace_limit_trips(
    enable_limiter: None,
    monkeypatch: pytest.MonkeyPatch,
    http: AsyncClient,
) -> None:
    """Per-workspace invitation limit trips after the configured threshold.

    20/hour is too many for a fast test; the route reads
    `settings.rate_limit_invites_per_workspace` at decorator-eval time so we
    can't shrink it via monkeypatch after import. Instead we send the full
    20 then assert the 21st is rate-limited.
    """
    _ = monkeypatch  # reserved for future shrinking once the limit is config-driven at call time
    await signup_owner(http)
    for i in range(20):
        r = await http.post(
            "/api/v1/workspaces/me/invitations",
            json={"email": f"invitee{i}@example.com", "role": "member"},
            headers=csrf_headers(http),
        )
        assert r.status_code in {200, 409}, r.text  # conflict if dup; we use unique emails
    r = await http.post(
        "/api/v1/workspaces/me/invitations",
        json={"email": "extra@example.com", "role": "member"},
        headers=csrf_headers(http),
    )
    _assert_rate_limited(r)
