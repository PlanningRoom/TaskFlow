"""Phase E3 — real Postgres LISTEN/NOTIFY round-trip through `broadcaster`.

The WS integration tests use a `memory://` broadcaster; this test proves the
Postgres backend itself ferries a message from a publisher to a subscriber
without going through the WebSocket layer.
"""

from __future__ import annotations

import asyncio
import os

import pytest
from broadcaster import Broadcast

pytestmark = pytest.mark.asyncio


def _postgres_dsn() -> str:
    """Translate the asyncpg test URL to broadcaster's `postgres://` form."""
    default = (
        "postgresql+asyncpg://taskflow:taskflow"  # pragma: allowlist secret
        "@localhost:5432/taskflow_test"
    )
    url = os.environ.get("TEST_DATABASE_URL", default)
    return url.replace("postgresql+asyncpg://", "postgres://", 1)


async def test_listen_notify_round_trip(db_engine: None) -> None:
    channel = "taskflow_test_roundtrip"
    publisher = Broadcast(_postgres_dsn())
    subscriber = Broadcast(_postgres_dsn())
    await publisher.connect()
    await subscriber.connect()
    try:
        async with subscriber.subscribe(channel=channel) as sub:
            # Tiny delay so the LISTEN registers before we publish.
            await asyncio.sleep(0.1)
            await publisher.publish(channel=channel, message='{"hello":"world"}')
            event = await asyncio.wait_for(sub.get(), timeout=2.0)
            assert event.message == '{"hello":"world"}'
    finally:
        await publisher.disconnect()
        await subscriber.disconnect()
