"""WebSocket endpoint at root `/ws` (TDD §10.1).

Authenticates via the session cookie + CSRF query param (ADR 051), subscribes
the connection to `user:{id}`, `workspace:{id}`, and one `project:{id}` per
accessible project, and fans broadcaster messages out to the client.

Close codes (per RFC 6455 application-defined range 4000-4999):
  4401 — unauthenticated (no/invalid session)
  4403 — CSRF check failed
  4500 — unexpected server error during setup
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from typing import Any

import structlog
from fastapi import WebSocket
from sqlalchemy import select
from starlette.websockets import WebSocketDisconnect, WebSocketState

from taskflow.auth.csrf import csrf_check
from taskflow.auth.sessions import lookup_session
from taskflow.db.models.session import Session as SessionModel
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace
from taskflow.db.session import session_scope
from taskflow.realtime.bus import get_broadcaster, is_initialized
from taskflow.realtime.channels import (
    project_channel,
    user_channel,
    workspace_channel,
)
from taskflow.services.projects import list_visible_projects
from taskflow.settings import settings

logger = structlog.get_logger()

CODE_UNAUTHENTICATED = 4401
CODE_CSRF_FAILED = 4403
CODE_SERVER_ERROR = 4500


async def _authenticate(
    websocket: WebSocket,
) -> tuple[SessionModel, User, Workspace] | None:
    """Validate session + CSRF and load identity. Closes the socket on failure."""
    raw_session = websocket.cookies.get(settings.session_cookie_name)
    csrf_query = websocket.query_params.get("csrf")
    csrf_cookie = websocket.cookies.get(settings.csrf_cookie_name)

    if not raw_session:
        await websocket.close(code=CODE_UNAUTHENTICATED, reason="missing session")
        return None

    async with session_scope() as db:
        session = await lookup_session(db, raw_session)
        if session is None:
            await websocket.close(code=CODE_UNAUTHENTICATED, reason="invalid session")
            return None

        # Treat the WS upgrade as a state-changing request (ADR 051).
        if not csrf_check(
            "POST",
            header_token=csrf_query,
            cookie_token=csrf_cookie,
            session=session,
        ):
            await websocket.close(code=CODE_CSRF_FAILED, reason="csrf failed")
            return None

        user = await db.scalar(select(User).where(User.id == session.user_id))
        if user is None or user.deleted_at is not None:
            await websocket.close(code=CODE_UNAUTHENTICATED, reason="user not found")
            return None
        workspace = await db.scalar(select(Workspace).where(Workspace.id == user.workspace_id))
        if workspace is None:
            await websocket.close(code=CODE_UNAUTHENTICATED, reason="workspace not found")
            return None

        # Persist the session.last_seen_at refresh that lookup_session applied.
        await db.commit()

    return session, user, workspace


async def _enumerate_project_channels(user: User) -> set[str]:
    async with session_scope() as db:
        projects = await list_visible_projects(db, user=user)
    return {project_channel(p.id) for p in projects}


async def _subscribe_and_relay(
    websocket: WebSocket,
    channel: str,
    out_queue: asyncio.Queue[tuple[str, str]],
) -> None:
    """Subscribe to one channel; push received messages into a shared queue."""
    bus = get_broadcaster()
    async with bus.subscribe(channel=channel) as subscriber:
        while True:
            event = await subscriber.get()
            await out_queue.put((channel, event.message))


async def _reader_loop(
    websocket: WebSocket,
    refresh_event: asyncio.Event,
) -> None:
    """Handle control messages from the client.

    Two control message types:
      - `{"type": "ping"}`                 → reply with pong
      - `{"type": "refresh_subscriptions"}` → outer loop re-enumerates projects
    """
    while True:
        try:
            text = await websocket.receive_text()
        except WebSocketDisconnect:
            return
        try:
            msg = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not isinstance(msg, dict):
            continue
        kind = msg.get("type")
        if kind == "ping":
            await websocket.send_text(json.dumps({"type": "pong"}))
        elif kind == "refresh_subscriptions":
            refresh_event.set()


async def _writer_loop(
    websocket: WebSocket,
    out_queue: asyncio.Queue[tuple[str, str]],
) -> None:
    """Drain the fan-in queue, forwarding envelopes to the client."""
    while True:
        _channel, message = await out_queue.get()
        if websocket.client_state != WebSocketState.CONNECTED:
            return
        await websocket.send_text(message)


async def websocket_endpoint(websocket: WebSocket) -> None:
    """Entry point — registered on the FastAPI app via `add_api_websocket_route`."""
    if not settings.realtime_enabled or not is_initialized():
        # Broadcaster isn't initialized — accept then close. (Tests run without it.)
        await websocket.close(code=CODE_SERVER_ERROR, reason="realtime disabled")
        return

    auth = await _authenticate(websocket)
    if auth is None:
        return
    _session, user, workspace = auth

    out_queue: asyncio.Queue[tuple[str, str]] = asyncio.Queue()
    refresh_event = asyncio.Event()

    await websocket.accept()
    logger.info(
        "ws.connected",
        user_id=str(user.id),
        workspace_id=str(workspace.id),
    )

    # Compute initial channel set.
    project_channels = await _enumerate_project_channels(user)
    base_channels = {user_channel(user.id), workspace_channel(workspace.id)}

    try:
        while True:
            channels = base_channels | project_channels
            subscribe_tasks: list[asyncio.Task[None]] = []
            for ch in channels:
                subscribe_tasks.append(
                    asyncio.create_task(_subscribe_and_relay(websocket, ch, out_queue))
                )
            reader_task = asyncio.create_task(_reader_loop(websocket, refresh_event))
            writer_task = asyncio.create_task(_writer_loop(websocket, out_queue))
            refresh_task = asyncio.create_task(refresh_event.wait())

            done, _pending = await asyncio.wait(
                [*subscribe_tasks, reader_task, writer_task, refresh_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Tear down subscribers + reader/writer before resubscribing or exiting.
            for t in [*subscribe_tasks, reader_task, writer_task, refresh_task]:
                if not t.done():
                    t.cancel()
            for t in [*subscribe_tasks, reader_task, writer_task, refresh_task]:
                with contextlib.suppress(asyncio.CancelledError, Exception):
                    await t

            if refresh_task in done and refresh_event.is_set():
                refresh_event.clear()
                project_channels = await _enumerate_project_channels(user)
                continue

            # Reader / writer ended → client disconnected.
            return
    except WebSocketDisconnect:
        return
    except Exception:  # noqa: BLE001
        logger.exception("ws.unexpected_error")
        with contextlib.suppress(Exception):
            await websocket.close(code=CODE_SERVER_ERROR)
    finally:
        logger.info(
            "ws.disconnected",
            user_id=str(user.id),
            workspace_id=str(workspace.id),
        )


# Re-exported for tests that want to introspect close codes.
__all__: list[Any] = [
    "websocket_endpoint",
    "CODE_UNAUTHENTICATED",
    "CODE_CSRF_FAILED",
    "CODE_SERVER_ERROR",
]
