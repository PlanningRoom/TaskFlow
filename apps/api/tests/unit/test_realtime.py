"""Unit tests for the realtime helpers (no DB / no broadcaster connection)."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from broadcaster import Broadcast

from taskflow.realtime import bus as bus_module
from taskflow.realtime import publish as publish_module
from taskflow.realtime.after_commit import (
    AfterCommitPublishMiddleware,
    pending_publishes,
    schedule_publish,
)
from taskflow.realtime.channels import (
    project_channel,
    user_channel,
    workspace_channel,
)


def test_channel_keys_are_stable() -> None:
    uid = UUID("00000000-0000-0000-0000-000000000001")
    assert user_channel(uid) == "user:00000000-0000-0000-0000-000000000001"
    assert workspace_channel(uid) == "workspace:00000000-0000-0000-0000-000000000001"
    assert project_channel(uid) == "project:00000000-0000-0000-0000-000000000001"


def test_envelope_shape_matches_tdd_10_2() -> None:
    ws_id = uuid4()
    proj_id = uuid4()
    env = publish_module._build_envelope(
        event_type="task.updated",
        workspace_id=ws_id,
        project_id=proj_id,
        payload={"task_id": "abc"},
    )
    assert env["type"] == "task.updated"
    assert env["workspace_id"] == str(ws_id)
    assert env["project_id"] == str(proj_id)
    assert env["payload"] == {"task_id": "abc"}
    assert "emitted_at" in env
    # Must JSON-serialize cleanly (default handles UUID + datetime).
    encoded = json.dumps(env, default=publish_module._json_default)
    decoded = json.loads(encoded)
    assert decoded["type"] == "task.updated"


async def test_publish_event_swallows_when_uninitialized() -> None:
    """Pub/sub failures must not raise — clients reconcile via refetch."""
    bus_module._broadcaster = None  # ensure not initialized
    # Should NOT raise.
    await publish_module.publish_event(
        channel="user:x",
        event_type="test",
        workspace_id=None,
        project_id=None,
        payload={},
    )


async def test_publish_event_swallows_broadcaster_errors() -> None:
    """Even with a misbehaving broadcaster, publish_event never raises."""

    class BoomBroadcaster:
        async def publish(self, *, channel: str, message: str) -> None:
            raise RuntimeError("simulated outage")

    bus_module._broadcaster = BoomBroadcaster()  # type: ignore[assignment]
    try:
        await publish_module.publish_event(
            channel="user:x",
            event_type="test",
            workspace_id=None,
            project_id=None,
            payload={},
        )
    finally:
        bus_module._broadcaster = None


async def test_schedule_publish_accumulates_on_request_state() -> None:
    req = MagicMock()
    req.state = MagicMock(spec=[])  # no attributes initially
    called: list[str] = []

    async def fake_pub() -> None:
        called.append("ran")

    schedule_publish(req, fake_pub)
    schedule_publish(req, fake_pub)
    queue = pending_publishes(req)
    assert len(queue) == 2
    for fn in queue:
        await fn()
    assert called == ["ran", "ran"]


async def test_after_commit_middleware_drains_on_2xx() -> None:
    """ASGI middleware drains the publish queue when the response is 2xx."""
    drained: list[str] = []

    async def fake_pub() -> None:
        drained.append("ran")

    async def app(scope: Any, receive: Any, send: Any) -> None:
        # Stash a publish on scope state, mimicking endpoint behavior.
        scope.setdefault("state", {}).setdefault("pending_publishes", []).append(fake_pub)
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    middleware = AfterCommitPublishMiddleware(app)

    sent: list[dict[str, Any]] = []

    async def send(msg: Any) -> None:
        sent.append(msg)

    async def receive() -> Any:
        return {"type": "http.request"}

    await middleware({"type": "http", "state": {}}, receive, send)
    assert drained == ["ran"]


async def test_after_commit_middleware_drops_queue_on_error_response() -> None:
    """On 4xx/5xx the queue is intentionally dropped."""
    drained: list[str] = []

    async def fake_pub() -> None:
        drained.append("ran")

    async def app(scope: Any, receive: Any, send: Any) -> None:
        scope.setdefault("state", {}).setdefault("pending_publishes", []).append(fake_pub)
        await send({"type": "http.response.start", "status": 500, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    middleware = AfterCommitPublishMiddleware(app)

    async def send(msg: Any) -> None:
        pass

    async def receive() -> Any:
        return {"type": "http.request"}

    await middleware({"type": "http", "state": {}}, receive, send)
    assert drained == []


async def test_memory_broadcaster_roundtrip() -> None:
    """Sanity: the broadcaster lib works with memory:// for our channel pattern."""
    bus = Broadcast("memory://")
    await bus.connect()
    try:
        async with bus.subscribe(channel="user:abc") as subscriber:
            await bus.publish(channel="user:abc", message="hi")
            # The memory backend delivers immediately; get with timeout.
            event = await asyncio.wait_for(subscriber.get(), timeout=1.0)
            assert event.message == "hi"
    finally:
        await bus.disconnect()
