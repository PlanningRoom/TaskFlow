"""Activity-feed DTOs (PRD §13.2 / §14)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from taskflow.schemas.tasks import ProjectRefDTO
from taskflow.schemas.users import UserSummary


class ActivityEventDTO(BaseModel):
    id: UUID
    event_type: str
    actor: UserSummary | None
    subject_type: str
    subject_id: UUID
    project: ProjectRefDTO | None
    metadata: dict[str, Any]
    created_at: datetime


class ListActivityResponse(BaseModel):
    events: list[ActivityEventDTO]
    next_cursor: str | None
