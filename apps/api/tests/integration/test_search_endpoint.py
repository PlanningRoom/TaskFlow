"""Phase C7 — search endpoint (PRD §12.1, ADR 062)."""

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


async def _seed(http: AsyncClient) -> str:
    await signup_owner(http)
    headers = csrf_headers(http)
    project = (await http.post("/api/v1/projects", json={"name": "P"}, headers=headers)).json()
    pid = project["id"]
    await http.post(
        f"/api/v1/projects/{pid}/tasks",
        json={
            "title": "Fix authentication bug",
            "description": "Login screen broken.",
        },
        headers=headers,
    )
    await http.post(
        f"/api/v1/projects/{pid}/tasks",
        json={"title": "Improve dashboard", "description": "Performance work."},
        headers=headers,
    )
    return str(pid)


async def test_match_in_title(http: AsyncClient) -> None:
    await _seed(http)
    r = await http.get("/api/v1/search?q=authentication")
    assert r.status_code == 200
    titles = [res["title"] for res in r.json()["results"]]
    assert "Fix authentication bug" in titles


async def test_match_in_description(http: AsyncClient) -> None:
    await _seed(http)
    r = await http.get("/api/v1/search?q=performance")
    titles = [res["title"] for res in r.json()["results"]]
    assert "Improve dashboard" in titles


async def test_empty_query_returns_empty(http: AsyncClient) -> None:
    await _seed(http)
    r = await http.get("/api/v1/search?q=")
    assert r.status_code == 200
    assert r.json()["results"] == []


async def test_cancelled_excluded_by_default(http: AsyncClient) -> None:
    pid = await _seed(http)
    headers = csrf_headers(http)
    cancel_target = (
        await http.post(
            f"/api/v1/projects/{pid}/tasks",
            json={"title": "Old authentication"},
            headers=headers,
        )
    ).json()
    await http.patch(
        f"/api/v1/tasks/{cancel_target['id']}/status",
        json={"status": "cancelled"},
        headers=headers,
    )
    r = await http.get("/api/v1/search?q=authentication")
    titles = [res["title"] for res in r.json()["results"]]
    assert "Old authentication" not in titles
    assert "Fix authentication bug" in titles

    r2 = await http.get("/api/v1/search?q=authentication&include_cancelled=true")
    titles2 = [res["title"] for res in r2.json()["results"]]
    assert "Old authentication" in titles2


async def test_member_only_sees_accessible_projects(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(http)  # Owner's accessible project
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(
        db_session, workspace_id=owner.workspace_id, role="member", email="m@x.com"
    )
    async with auth_client(app, db_session, member) as client:
        r = await client.get("/api/v1/search?q=authentication")
        assert r.status_code == 200
        # Member has no project access; results filtered to empty.
        assert r.json()["results"] == []
