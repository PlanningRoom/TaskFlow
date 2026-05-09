"""Task DTOs (PRD §6, screen inventory §3.5 / §4.1)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from taskflow.schemas.labels import LabelDTO
from taskflow.schemas.users import UserSummary

TaskStatus = Literal["backlog", "todo", "in_progress", "in_review", "done", "cancelled"]
TaskPriority = Literal["none", "low", "medium", "high", "urgent"]
SortKey = Literal["created_desc", "priority", "due", "assignee"]
DueFilter = Literal["overdue", "today", "this_week", "none"]

TitleField = Annotated[str, Field(min_length=1, max_length=400)]
DescriptionField = Annotated[str, Field(max_length=20_000)]


class ProjectRefDTO(BaseModel):
    id: UUID
    name: str


class TaskSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    assignee: UserSummary | None
    labels: list[LabelDTO]
    comment_count: int
    project: ProjectRefDTO


class TaskDetail(TaskSummary):
    description: str | None
    created_at: datetime
    updated_at: datetime


class CreateTaskRequest(BaseModel):
    title: TitleField
    description: DescriptionField | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: UUID | None = None
    due_date: date | None = None
    label_ids: list[UUID] | None = None


class UpdateTaskRequest(BaseModel):
    title: TitleField | None = None
    description: DescriptionField | None = None
    priority: TaskPriority | None = None
    assignee_id: UUID | None = None
    # Sentinel: explicit `None` clears assignment; key omitted = leave alone.
    # Pydantic distinguishes via `model_fields_set`.
    due_date: date | None = None
    label_ids: list[UUID] | None = None


class UpdateStatusRequest(BaseModel):
    status: TaskStatus


class ListTasksResponse(BaseModel):
    tasks: list[TaskSummary]
    next_cursor: str | None
