"""Phase C1 — label endpoints (PRD §7, DRD §2.9)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.audit_log import AuditLog
from taskflow.db.models.label import Label
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


async def test_owner_can_create_label(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    response = await http.post(
        "/api/v1/labels",
        json={"name": "bug", "color": "red"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["name"] == "bug" and body["color"] == "red"

    label = await db_session.scalar(select(Label).where(Label.name == "bug"))
    assert label is not None

    audit = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "workspace.label.created")
    )
    assert audit is not None and audit.target_id == label.id


@pytest.mark.parametrize("role", ["member", "viewer"])
async def test_member_viewer_cannot_create_label(
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
            "/api/v1/labels",
            json={"name": "feature", "color": "blue"},
            headers=csrf_headers(client),
        )
        assert response.status_code == 403


async def test_invalid_color_rejected(http: AsyncClient) -> None:
    await signup_owner(http)
    response = await http.post(
        "/api/v1/labels",
        json={"name": "weird", "color": "chartreuse"},
        headers=csrf_headers(http),
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


async def test_duplicate_name_conflicts(http: AsyncClient) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    await http.post("/api/v1/labels", json={"name": "bug", "color": "red"}, headers=headers)
    response = await http.post(
        "/api/v1/labels", json={"name": "bug", "color": "blue"}, headers=headers
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "LABEL_NAME_TAKEN"


async def test_list_labels_visible_to_all_roles(
    app: FastAPI, http: AsyncClient, db_session: AsyncSession
) -> None:
    await signup_owner(http)
    await http.post(
        "/api/v1/labels",
        json={"name": "bug", "color": "red"},
        headers=csrf_headers(http),
    )
    owner = await db_session.scalar(select(User).where(User.role == "owner"))
    assert owner is not None
    viewer = await make_user(
        db_session, workspace_id=owner.workspace_id, role="viewer", email="v@x.com"
    )
    async with auth_client(app, db_session, viewer) as client:
        response = await client.get("/api/v1/labels")
        assert response.status_code == 200
        body = response.json()
        assert len(body["labels"]) == 1
        assert body["labels"][0]["name"] == "bug"


async def test_update_label(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    created = await http.post(
        "/api/v1/labels", json={"name": "bug", "color": "red"}, headers=headers
    )
    label_id = created.json()["id"]
    response = await http.patch(
        f"/api/v1/labels/{label_id}",
        json={"name": "defect", "color": "amber"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "defect" and body["color"] == "amber"

    audit = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "workspace.label.updated")
    )
    assert audit is not None


async def test_update_label_to_existing_name_conflicts(http: AsyncClient) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    await http.post("/api/v1/labels", json={"name": "bug", "color": "red"}, headers=headers)
    feature = (
        await http.post(
            "/api/v1/labels", json={"name": "feature", "color": "blue"}, headers=headers
        )
    ).json()

    # Renaming "feature" onto the existing "bug" name is rejected.
    response = await http.patch(
        f"/api/v1/labels/{feature['id']}",
        json={"name": "bug"},
        headers=headers,
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "LABEL_NAME_TAKEN"


async def test_delete_label_cascades_audit(http: AsyncClient, db_session: AsyncSession) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    created = await http.post(
        "/api/v1/labels", json={"name": "bug", "color": "red"}, headers=headers
    )
    label_id = created.json()["id"]
    response = await http.delete(f"/api/v1/labels/{label_id}", headers=headers)
    assert response.status_code == 200

    from uuid import UUID

    label = await db_session.scalar(select(Label).where(Label.id == UUID(label_id)))
    assert label is None

    audit = await db_session.scalar(
        select(AuditLog).where(AuditLog.event_type == "workspace.label.deleted")
    )
    assert audit is not None
