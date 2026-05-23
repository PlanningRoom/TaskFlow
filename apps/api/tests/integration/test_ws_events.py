"""End-to-end: drive each event type via the HTTP API while a WS is open;
assert the envelope arrives with the TDD §10.2 shape.

All tests in this file require Postgres (auto-skipped when unreachable).
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from broadcaster import Broadcast
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.realtime import bus as bus_module
from taskflow.settings import settings
from tests.integration._helpers import OWNER_PAYLOAD


@pytest_asyncio.fixture
async def _bus() -> AsyncIterator[Broadcast]:
    bus = Broadcast("memory://")
    await bus.connect()
    bus_module._broadcaster = bus
    yield bus
    bus_module._broadcaster = None
    await bus.disconnect()


@pytest.fixture
def ws_client(_bus: Broadcast) -> Iterator[TestClient]:
    with (
        patch("taskflow.main.init_broadcaster", new=AsyncMock(return_value=_bus)),
        patch("taskflow.main.dispose_broadcaster", new=AsyncMock()),
    ):
        from taskflow.main import app

        with TestClient(app, raise_server_exceptions=False) as tc:
            yield tc


def _drain_until(ws: Any, expected_type: str, timeout: float = 2.0) -> dict[str, Any]:
    """Read frames until one matches `expected_type` or budget exhausted."""
    deadline_frames = 20
    for _ in range(deadline_frames):
        raw = ws.receive_text()
        env: dict[str, Any] = json.loads(raw)
        if env.get("type") == expected_type:
            return env
    raise AssertionError(f"never received {expected_type!r}")


async def test_task_created_envelope_arrives(
    db_engine: None,
    db_session: AsyncSession,
    ws_client: TestClient,
) -> None:
    # Signup → create project → open WS → create task → assert envelope.
    r = ws_client.post("/api/v1/auth/signup", json=OWNER_PAYLOAD)
    assert r.status_code == 200
    csrf = ws_client.cookies.get(settings.csrf_cookie_name)
    assert csrf is not None
    csrf_headers = {settings.csrf_header_name: csrf}

    pr = ws_client.post(
        "/api/v1/projects",
        json={"name": "P1", "description": None, "color": "blue"},
        headers=csrf_headers,
    )
    assert pr.status_code == 200
    project_id = pr.json()["id"]

    with ws_client.websocket_connect(f"/ws?csrf={csrf}") as ws:
        tr = ws_client.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "First task"},
            headers=csrf_headers,
        )
        assert tr.status_code == 200

        env = _drain_until(ws, "task.created")
        assert env["project_id"] == project_id
        assert env["payload"]["task_id"] == tr.json()["id"]
        assert "emitted_at" in env


async def test_workspace_isolation_no_leakage(
    db_engine: None,
    db_session: AsyncSession,
    ws_client: TestClient,
) -> None:
    """A user in workspace A must NOT receive events from workspace B."""
    # Workspace A: signup, get csrf
    r = ws_client.post("/api/v1/auth/signup", json=OWNER_PAYLOAD)
    assert r.status_code == 200
    a_csrf = ws_client.cookies.get(settings.csrf_cookie_name)
    a_session = ws_client.cookies.get(settings.session_cookie_name)
    assert a_csrf and a_session

    pr = ws_client.post(
        "/api/v1/projects",
        json={"name": "P-A", "description": None, "color": "blue"},
        headers={settings.csrf_header_name: a_csrf},
    )
    a_project_id = pr.json()["id"]

    # Workspace B signup (using a fresh client to avoid cookie collisions)
    ws_client.cookies.clear()
    b_payload = {**OWNER_PAYLOAD, "email": "b-owner@example.com"}
    r2 = ws_client.post("/api/v1/auth/signup", json=b_payload)
    assert r2.status_code == 200
    b_csrf = ws_client.cookies.get(settings.csrf_cookie_name)
    b_session = ws_client.cookies.get(settings.session_cookie_name)
    assert b_csrf and b_session

    # B opens a WS. A then creates a task in their workspace. B must not see it.
    ws_client.cookies.set(settings.session_cookie_name, b_session)
    ws_client.cookies.set(settings.csrf_cookie_name, b_csrf)
    with ws_client.websocket_connect(f"/ws?csrf={b_csrf}") as ws_b:
        # A creates a task
        ws_client.cookies.set(settings.session_cookie_name, a_session)
        ws_client.cookies.set(settings.csrf_cookie_name, a_csrf)
        tr = ws_client.post(
            f"/api/v1/projects/{a_project_id}/tasks",
            json={"title": "A's task"},
            headers={settings.csrf_header_name: a_csrf},
        )
        assert tr.status_code == 200

        # Send a ping to B's socket and expect pong (no task.created in between)
        ws_b.send_text('{"type": "ping"}')
        reply = json.loads(ws_b.receive_text())
        # If A's event leaked, this would be type="task.created" instead.
        assert reply["type"] == "pong", f"leakage: {reply}"


async def test_comment_created_envelope_arrives(
    db_engine: None,
    db_session: AsyncSession,
    ws_client: TestClient,
) -> None:
    r = ws_client.post("/api/v1/auth/signup", json=OWNER_PAYLOAD)
    assert r.status_code == 200
    csrf = ws_client.cookies.get(settings.csrf_cookie_name)
    assert csrf is not None
    csrf_headers = {settings.csrf_header_name: csrf}

    pr = ws_client.post(
        "/api/v1/projects",
        json={"name": "P1", "description": None, "color": "blue"},
        headers=csrf_headers,
    )
    project_id = pr.json()["id"]
    tr = ws_client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T1"},
        headers=csrf_headers,
    )
    task_id = tr.json()["id"]

    with ws_client.websocket_connect(f"/ws?csrf={csrf}") as ws:
        cr = ws_client.post(
            f"/api/v1/tasks/{task_id}/comments",
            json={"body": "Hello!"},
            headers=csrf_headers,
        )
        assert cr.status_code == 200

        env = _drain_until(ws, "comment.created")
        assert env["payload"]["task_id"] == task_id


async def test_task_status_changed_envelope_arrives(
    db_engine: None,
    db_session: AsyncSession,
    ws_client: TestClient,
) -> None:
    assert ws_client.post("/api/v1/auth/signup", json=OWNER_PAYLOAD).status_code == 200
    csrf = ws_client.cookies.get(settings.csrf_cookie_name)
    assert csrf is not None
    csrf_headers = {settings.csrf_header_name: csrf}
    pr = ws_client.post(
        "/api/v1/projects",
        json={"name": "P1", "description": None, "color": "blue"},
        headers=csrf_headers,
    )
    project_id = pr.json()["id"]
    tr = ws_client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "T1"},
        headers=csrf_headers,
    )
    task_id = tr.json()["id"]

    with ws_client.websocket_connect(f"/ws?csrf={csrf}") as ws:
        sr = ws_client.patch(
            f"/api/v1/tasks/{task_id}/status",
            json={"status": "in_progress"},
            headers=csrf_headers,
        )
        assert sr.status_code == 200
        env = _drain_until(ws, "task.status_changed")
        assert env["payload"]["from"] == "backlog"
        assert env["payload"]["to"] == "in_progress"
