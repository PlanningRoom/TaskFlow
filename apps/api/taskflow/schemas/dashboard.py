"""Dashboard DTOs (PRD §13, screen inventory §3.4)."""

from __future__ import annotations

from pydantic import BaseModel

from taskflow.schemas.tasks import ProjectRefDTO, TaskSummary


class TaskCounts(BaseModel):
    backlog: int = 0
    todo: int = 0
    in_progress: int = 0
    in_review: int = 0
    done: int = 0
    cancelled: int = 0


class MyTaskGroup(BaseModel):
    project: ProjectRefDTO
    tasks: list[TaskSummary]


class MyTasksResponse(BaseModel):
    groups: list[MyTaskGroup]


class DashboardProjectDTO(BaseModel):
    id: str
    name: str
    color: str | None
    task_counts: TaskCounts


class DashboardProjectsResponse(BaseModel):
    projects: list[DashboardProjectDTO]
