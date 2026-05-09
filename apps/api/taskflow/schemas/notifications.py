"""Notification DTOs (PRD §15, ADR 064/070)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel

from taskflow.schemas.tasks import ProjectRefDTO
from taskflow.schemas.users import UserSummary

NotificationEventType = Literal["mention", "task_assigned", "task_status_changed", "task_commented"]


class NotificationTaskRefDTO(BaseModel):
    id: UUID
    title: str
    project: ProjectRefDTO


class NotificationDTO(BaseModel):
    id: UUID
    event_type: NotificationEventType
    actor: UserSummary | None
    task: NotificationTaskRefDTO | None
    metadata: dict[str, Any]
    created_at: datetime
    read_at: datetime | None


class ListNotificationsResponse(BaseModel):
    notifications: list[NotificationDTO]
    next_cursor: str | None


class UnreadCountResponse(BaseModel):
    count: int
