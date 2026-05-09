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
    # Human-readable detail string for the UI sentence (e.g. "to In Review",
    # task title, comment preview). Derived from event_type + metadata at
    # hydration time so the frontend can render without a name table.
    detail: str | None
    metadata: dict[str, Any]
    created_at: datetime


class ListActivityResponse(BaseModel):
    events: list[ActivityEventDTO]
    next_cursor: str | None
