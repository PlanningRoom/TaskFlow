"""Phase E2 — WebSocket connection gauge emitter."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from taskflow.api.v1 import ws


def test_gauge_emits_with_current_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """`emit_websocket_connections_gauge` calls `logger.info` with the gauge
    value. We swap the module-level `logger` for a `MagicMock` so the assertion
    works regardless of whether structlog is configured (which differs between
    isolated unit runs and the post-integration test ordering)."""
    fake_logger = MagicMock()
    monkeypatch.setattr(ws, "logger", fake_logger)
    ws._ws_active_connections = 3
    try:
        ws.emit_websocket_connections_gauge()
    finally:
        ws._ws_active_connections = 0

    fake_logger.info.assert_called_once()
    args: tuple[Any, ...] = fake_logger.info.call_args.args
    kwargs: dict[str, Any] = fake_logger.info.call_args.kwargs
    assert args[0] == "websocket_connections"
    assert kwargs["value"] == 3


def test_active_connections_returns_current() -> None:
    ws._ws_active_connections = 7
    try:
        assert ws.active_connections() == 7
    finally:
        ws._ws_active_connections = 0
