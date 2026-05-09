"""Search DTOs (PRD §12.1, ADR 062)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from taskflow.schemas.tasks import ProjectRefDTO, TaskStatus


class SearchResult(BaseModel):
    task_id: UUID
    title: str
    status: TaskStatus
    project: ProjectRefDTO


class SearchResponse(BaseModel):
    results: list[SearchResult]
