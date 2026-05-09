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
