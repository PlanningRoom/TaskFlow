"""Publish helper: builds the TDD §10.2 envelope and emits via broadcaster.

Delivery is at-most-once (TDD §10.4): we log-and-swallow publish failures so a
pub/sub blip cannot fail an otherwise-successful HTTP response. Clients
reconcile via refetch on reconnect.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, TypedDict
from uuid import UUID

import structlog

from taskflow.realtime.bus import get_broadcaster, is_initialized
from taskflow.realtime.channels import (
    project_channel,
    user_channel,
    workspace_channel,
)
from taskflow.settings import settings

logger = structlog.get_logger()


class Envelope(TypedDict):
    type: str
    workspace_id: str | None
    project_id: str | None
    payload: dict[str, Any]
    emitted_at: str


def _json_default(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _build_envelope(
    *,
    event_type: str,
    workspace_id: UUID | None,
    project_id: UUID | None,
    payload: dict[str, Any],
) -> Envelope:
    return Envelope(
        type=event_type,
        workspace_id=str(workspace_id) if workspace_id else None,
        project_id=str(project_id) if project_id else None,
        payload=payload,
        emitted_at=datetime.now(UTC).isoformat(),
    )


async def publish_event(
    *,
    channel: str,
    event_type: str,
    workspace_id: UUID | None,
    project_id: UUID | None,
    payload: dict[str, Any],
) -> None:
    """Publish an envelope to a channel. Never raises."""
    if not settings.realtime_enabled or not is_initialized():
        return
    envelope = _build_envelope(
        event_type=event_type,
        workspace_id=workspace_id,
        project_id=project_id,
        payload=payload,
    )
    try:
        encoded = json.dumps(envelope, default=_json_default)
        await get_broadcaster().publish(channel=channel, message=encoded)
    except Exception as exc:  # noqa: BLE001 — pub/sub failures must not break HTTP
        logger.warning(
            "realtime.publish_failed",
            channel=channel,
            event_type=event_type,
            error=str(exc),
        )


async def publish_to_user(
    *,
    user_id: UUID,
    event_type: str,
    workspace_id: UUID | None,
    payload: dict[str, Any],
) -> None:
    await publish_event(
        channel=user_channel(user_id),
        event_type=event_type,
        workspace_id=workspace_id,
        project_id=None,
        payload=payload,
    )


async def publish_to_workspace(
    *,
    workspace_id: UUID,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    await publish_event(
        channel=workspace_channel(workspace_id),
        event_type=event_type,
        workspace_id=workspace_id,
        project_id=None,
        payload=payload,
    )


async def publish_to_project(
    *,
    project_id: UUID,
    workspace_id: UUID,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    await publish_event(
        channel=project_channel(project_id),
        event_type=event_type,
        workspace_id=workspace_id,
        project_id=project_id,
        payload=payload,
    )
