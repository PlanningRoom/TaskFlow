"""WebSocket authentication + CSRF close codes (TDD §10.1, ADR 051)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from broadcaster import Broadcast
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect

from taskflow.api.v1.ws import CODE_CSRF_FAILED, CODE_UNAUTHENTICATED
from taskflow.realtime import bus as bus_module
from taskflow.settings import settings
from tests.integration._helpers import OWNER_PAYLOAD, make_user


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
    """TestClient with the broadcaster pre-initialized in-memory."""
    with (
        patch("taskflow.main.init_broadcaster", new=AsyncMock(return_value=_bus)),
        patch("taskflow.main.dispose_broadcaster", new=AsyncMock()),
    ):
        from taskflow.main import app

        with TestClient(app, raise_server_exceptions=False) as tc:
            yield tc


async def test_missing_session_cookie_closes_4401(db_engine: None, ws_client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as exc:
        with ws_client.websocket_connect("/ws"):
            pass
    assert exc.value.code == CODE_UNAUTHENTICATED


async def test_invalid_session_cookie_closes_4401(db_engine: None, ws_client: TestClient) -> None:
    ws_client.cookies.set(settings.session_cookie_name, "not-a-real-session-token")
    with pytest.raises(WebSocketDisconnect) as exc:
        with ws_client.websocket_connect("/ws"):
            pass
    assert exc.value.code == CODE_UNAUTHENTICATED


async def test_missing_csrf_query_param_closes_4403(
    db_engine: None,
    db_session: AsyncSession,
    ws_client: TestClient,
) -> None:
    # Sign up via HTTP so the session cookie is real.
    r = ws_client.post("/api/v1/auth/signup", json=OWNER_PAYLOAD)
    assert r.status_code == 200
    with pytest.raises(WebSocketDisconnect) as exc:
        with ws_client.websocket_connect("/ws"):  # no ?csrf=...
            pass
    assert exc.value.code == CODE_CSRF_FAILED


async def test_mismatched_csrf_closes_4403(
    db_engine: None,
    db_session: AsyncSession,
    ws_client: TestClient,
) -> None:
    r = ws_client.post("/api/v1/auth/signup", json=OWNER_PAYLOAD)
    assert r.status_code == 200
    with pytest.raises(WebSocketDisconnect) as exc:
        with ws_client.websocket_connect("/ws?csrf=not-the-right-token"):
            pass
    assert exc.value.code == CODE_CSRF_FAILED


async def test_happy_path_connects_and_pongs(
    db_engine: None,
    db_session: AsyncSession,
    ws_client: TestClient,
) -> None:
    r = ws_client.post("/api/v1/auth/signup", json=OWNER_PAYLOAD)
    assert r.status_code == 200
    csrf = ws_client.cookies.get(settings.csrf_cookie_name)
    assert csrf is not None
    with ws_client.websocket_connect(f"/ws?csrf={csrf}") as ws:
        ws.send_text('{"type": "ping"}')
        import json

        reply = json.loads(ws.receive_text())
        assert reply == {"type": "pong"}


async def test_deleted_user_cannot_connect(
    db_engine: None,
    db_session: AsyncSession,
    ws_client: TestClient,
) -> None:
    # Sign up as owner, then mark the user deleted_at to simulate anonymization.
    r = ws_client.post("/api/v1/auth/signup", json=OWNER_PAYLOAD)
    assert r.status_code == 200
    csrf = ws_client.cookies.get(settings.csrf_cookie_name)
    assert csrf is not None

    from datetime import UTC, datetime

    from sqlalchemy import update

    from taskflow.db.models.user import User

    await db_session.execute(
        update(User)
        .where(User.email == OWNER_PAYLOAD["email"])
        .values(deleted_at=datetime.now(UTC))
    )
    await db_session.commit()

    with pytest.raises(WebSocketDisconnect) as exc:
        with ws_client.websocket_connect(f"/ws?csrf={csrf}"):
            pass
    assert exc.value.code == CODE_UNAUTHENTICATED


# Avoid "unused" warning on the helper import used elsewhere.
_ = make_user
