"""Dashboard endpoints (Phase C8, PRD §13)."""

from __future__ import annotations

from fastapi import APIRouter

from taskflow.api.v1.tasks import _summary_from_hydrated
from taskflow.auth.dependencies import DbDep, UserDep
from taskflow.schemas.dashboard import (
    DashboardProjectDTO,
    DashboardProjectsResponse,
    MyTaskGroup,
    MyTasksResponse,
    TaskCounts,
)
from taskflow.schemas.tasks import ProjectRefDTO
from taskflow.services import dashboard as dashboard_service
from taskflow.services import tasks as task_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/my-tasks", response_model=MyTasksResponse)
async def my_tasks_endpoint(db: DbDep, user: UserDep) -> MyTasksResponse:
    groups = await dashboard_service.my_tasks(db, user=user)
    out = []
    for project, tasks in groups:
        summaries = [
            _summary_from_hydrated(await task_service.hydrate_task(db, task=t)) for t in tasks
        ]
        out.append(
            MyTaskGroup(
                project=ProjectRefDTO(id=project.id, name=project.name),
                tasks=summaries,
            )
        )
    return MyTasksResponse(groups=out)


@router.get("/projects", response_model=DashboardProjectsResponse)
async def dashboard_projects_endpoint(db: DbDep, user: UserDep) -> DashboardProjectsResponse:
    pairs = await dashboard_service.projects_with_counts(db, user=user)
    items = [
        DashboardProjectDTO(
            id=str(p.id),
            name=p.name,
            color=p.color,
            task_counts=TaskCounts(
                backlog=counts.get("backlog", 0),
                todo=counts.get("todo", 0),
                in_progress=counts.get("in_progress", 0),
                in_review=counts.get("in_review", 0),
                done=counts.get("done", 0),
                cancelled=counts.get("cancelled", 0),
            ),
        )
        for p, counts in pairs
    ]
    return DashboardProjectsResponse(projects=items)
