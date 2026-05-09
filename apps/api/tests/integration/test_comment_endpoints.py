"""Phase C4 — comment endpoints (PRD §11, ADR 088)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.activity_event import ActivityEvent
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


async def _make_task(http: AsyncClient) -> str:
    headers = csrf_headers(http)
    project = (await http.post("/api/v1/projects", json={"name": "P"}, headers=headers)).json()
    task = (
        await http.post(
            f"/api/v1/projects/{project['id']}/tasks",
            json={"title": "T"},
            headers=headers,
        )
    ).json()
    return str(task["id"])


async def test_owner_can_post_comment(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    task_id = await _make_task(http)
    response = await http.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"body": "Looks good"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["body"] == "Looks good"
    assert body["author"]["display_name"] == "Aurora Owner"
    assert body["mentions"] == []

    activity = await db_session.scalar(
        select(ActivityEvent).where(ActivityEvent.event_type == "comment.created")
    )
    assert activity is not None


async def test_viewer_cannot_post_comment(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    task_id = await _make_task(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    viewer = await make_user(
        db_session, workspace_id=owner.workspace_id, role="viewer", email="v@x.com"
    )
    async with auth_client(app, db_session, viewer) as client:
        r = await client.post(
            f"/api/v1/tasks/{task_id}/comments",
            json={"body": "Forbidden"},
            headers=csrf_headers(client),
        )
        assert r.status_code == 403


async def test_mention_resolves_workspace_member(
    http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    member = await make_user(
        db_session,
        workspace_id=owner.workspace_id,
        role="member",
        email="m@x.com",
        name="Mable Member",
    )
    task_id = await _make_task(http)
    response = await http.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"body": "Hi @mable-member can you look?"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["mentions"]) == 1
    assert body["mentions"][0]["id"] == str(member.id)


async def test_unknown_mention_drops(http: AsyncClient) -> None:
    await signup_owner(http)
    task_id = await _make_task(http)
    response = await http.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"body": "Hi @nobody"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200
    assert response.json()["mentions"] == []


async def test_author_can_edit_own_comment(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    task_id = await _make_task(http)
    headers = csrf_headers(http)
    posted = (
        await http.post(
            f"/api/v1/tasks/{task_id}/comments",
            json={"body": "Original"},
            headers=headers,
        )
    ).json()
    response = await http.patch(
        f"/api/v1/comments/{posted['id']}",
        json={"body": "Edited"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["body"] == "Edited"


async def test_non_author_cannot_edit_comment(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    task_id = await _make_task(http)
    posted = (
        await http.post(
            f"/api/v1/tasks/{task_id}/comments",
            json={"body": "Original"},
            headers=csrf_headers(http),
        )
    ).json()

    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    admin = await make_user(
        db_session, workspace_id=owner.workspace_id, role="admin", email="a@x.com"
    )
    async with auth_client(app, db_session, admin) as client:
        r = await client.patch(
            f"/api/v1/comments/{posted['id']}",
            json={"body": "hijack"},
            headers=csrf_headers(client),
        )
        assert r.status_code == 403


async def test_author_can_delete_own_comment(
    http: AsyncClient,
) -> None:
    await signup_owner(http)
    task_id = await _make_task(http)
    headers = csrf_headers(http)
    posted = (
        await http.post(
            f"/api/v1/tasks/{task_id}/comments",
            json={"body": "Original"},
            headers=headers,
        )
    ).json()
    response = await http.delete(f"/api/v1/comments/{posted['id']}", headers=headers)
    assert response.status_code == 200

    listed = await http.get(f"/api/v1/tasks/{task_id}/comments")
    assert listed.json()["comments"] == []


async def test_list_comments_chronological(
    http: AsyncClient,
) -> None:
    await signup_owner(http)
    task_id = await _make_task(http)
    headers = csrf_headers(http)
    for body in ["First", "Second", "Third"]:
        await http.post(
            f"/api/v1/tasks/{task_id}/comments",
            json={"body": body},
            headers=headers,
        )
    response = await http.get(f"/api/v1/tasks/{task_id}/comments")
    bodies = [c["body"] for c in response.json()["comments"]]
    assert bodies == ["First", "Second", "Third"]


async def test_cross_workspace_comment_404(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    task_id = await _make_task(http)
    posted = (
        await http.post(
            f"/api/v1/tasks/{task_id}/comments",
            json={"body": "x"},
            headers=csrf_headers(http),
        )
    ).json()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as b_http:
        await signup_owner(
            b_http,
            payload={
                "email": "b@example.com",
                "password": "correct-horse-battery-staple-b",
                "display_name": "B",
                "workspace_name": "B",
            },
        )
        r = await b_http.patch(
            f"/api/v1/comments/{posted['id']}",
            json={"body": "stolen"},
            headers=csrf_headers(b_http),
        )
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "COMMENT_NOT_FOUND"
