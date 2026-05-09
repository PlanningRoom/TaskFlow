"""Notification DTOs (PRD §15, ADR 064/070, screen inventory §3.7)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel

from taskflow.schemas.tasks import ProjectRefDTO
from taskflow.schemas.users import UserSummary

# DB CHECK constraint pins these (ADR 064). The screen inventory's enum
# names diverge — the canonical names are these, and the frontend can map
# them cosmetically.
NotificationEventType = Literal["mention", "task_assigned", "task_status_changed", "task_commented"]


class NotificationTaskRefDTO(BaseModel):
    id: UUID
    title: str


class NotificationDTO(BaseModel):
    id: UUID
    event_type: NotificationEventType
    actor: UserSummary | None
    task: NotificationTaskRefDTO | None
    project: ProjectRefDTO | None
    detail: str | None
    read: bool
    created_at: datetime
    read_at: datetime | None
    metadata: dict[str, Any]


class ListNotificationsResponse(BaseModel):
    notifications: list[NotificationDTO]
    next_cursor: str | None


class UnreadCountResponse(BaseModel):
    count: int
