"""Broadcaster lifecycle (ADR 045).

Wraps the `broadcaster` Python library with the Postgres LISTEN/NOTIFY backend.
The singleton is initialized inside the FastAPI lifespan and disposed on
shutdown — mirroring the engine pattern in `db/session.py`.
"""

from __future__ import annotations

import structlog
from broadcaster import Broadcast

from taskflow.settings import settings

logger = structlog.get_logger()

_broadcaster: Broadcast | None = None


def _postgres_url() -> str:
    """Translate the SQLAlchemy URL to the form broadcaster expects.

    SQLAlchemy uses `postgresql+asyncpg://...`; broadcaster's postgres backend
    just wants `postgres://...` (or `postgresql://...`). Strip the driver tag.
    """
    url = settings.database_url
    if url.startswith("postgresql+asyncpg://"):
        return "postgres://" + url[len("postgresql+asyncpg://") :]
    if url.startswith("postgresql://"):
        return "postgres://" + url[len("postgresql://") :]
    return url


async def init_broadcaster() -> Broadcast | None:
    """Create + connect the broadcaster singleton. Idempotent.

    Returns None when `realtime_enabled=False` (tests, perf runs, etc.).
    """
    global _broadcaster
    if _broadcaster is not None:
        return _broadcaster
    if not settings.realtime_enabled:
        logger.info("broadcaster.disabled", reason="realtime_enabled=False")
        return None
    bus = Broadcast(_postgres_url())
    await bus.connect()
    _broadcaster = bus
    logger.info("broadcaster.connected")
    return bus


def get_broadcaster() -> Broadcast:
    """Return the connected broadcaster. Raises if not initialized."""
    if _broadcaster is None:
        raise RuntimeError(
            "Broadcaster is not initialized. Call init_broadcaster() in the lifespan."
        )
    return _broadcaster


def is_initialized() -> bool:
    return _broadcaster is not None


async def dispose_broadcaster() -> None:
    """Disconnect and clear the singleton. Idempotent."""
    global _broadcaster
    if _broadcaster is None:
        return
    try:
        await _broadcaster.disconnect()
    finally:
        _broadcaster = None
        logger.info("broadcaster.disconnected")
