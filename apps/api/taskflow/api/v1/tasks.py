"""Task endpoints (Phase C3)."""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from taskflow.auth.dependencies import (
    DbDep,
    UserDep,
    require_action,
    require_project_access,
    verify_csrf,
)
from taskflow.auth.permissions import Action
from taskflow.db.models.task import Task
from taskflow.schemas.labels import LabelDTO
from taskflow.schemas.tasks import (
    CreateTaskRequest,
    ListTasksResponse,
    ProjectRefDTO,
    TaskDetail,
    TaskSummary,
    UpdateStatusRequest,
    UpdateTaskRequest,
)
from taskflow.services import tasks as task_service

router = APIRouter(tags=["tasks"])


def _summary_from_hydrated(hydrated: dict[str, Any]) -> TaskSummary:
    task: Task = hydrated["task"]
    project = hydrated["project"]
    return TaskSummary(
        id=task.id,
        title=task.title,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        assignee=hydrated["assignee"],
        labels=[LabelDTO.model_validate(lbl) for lbl in hydrated["labels"]],
        comment_count=hydrated["comment_count"],
        project=ProjectRefDTO(id=project.id, name=project.name),
    )


def _detail_from_hydrated(hydrated: dict[str, Any]) -> TaskDetail:
    task: Task = hydrated["task"]
    summary = _summary_from_hydrated(hydrated)
    return TaskDetail(
        **summary.model_dump(),
        description=task.description,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Project-scoped list / create
# ──────────────────────────────────────────────────────────────────────────────


@router.get(
    "/projects/{project_id}/tasks",
    response_model=ListTasksResponse,
    dependencies=[Depends(require_project_access())],
)
async def list_project_tasks(
    project_id: UUID,
    db: DbDep,
    user: UserDep,
    status: Annotated[list[str] | None, Query()] = None,
    assignee: Annotated[list[UUID] | None, Query()] = None,
    priority: Annotated[list[str] | None, Query()] = None,
    label: Annotated[list[UUID] | None, Query()] = None,
    due: str | None = None,
    include_cancelled: bool = False,
    sort: str = "created_desc",
    cursor: str | None = None,
    limit: int = task_service.DEFAULT_LIMIT,
) -> ListTasksResponse:
    rows, next_cursor = await task_service.list_tasks(
        db,
        project_id=project_id,
        workspace_id=user.workspace_id,
        status=status,
        assignees=assignee,
        priorities=priority,
        label_ids=label,
        due=due,
        include_cancelled=include_cancelled,
        sort=sort,
        cursor=cursor,
        limit=limit,
    )
    summaries = [_summary_from_hydrated(await task_service.hydrate_task(db, task=t)) for t in rows]
    return ListTasksResponse(tasks=summaries, next_cursor=next_cursor)


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskDetail,
    dependencies=[
        Depends(verify_csrf),
        Depends(require_action(Action.CREATE_TASK)),
        Depends(require_project_access()),
    ],
)
async def create_project_task(
    project_id: UUID,
    body: CreateTaskRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
) -> TaskDetail:
    task = await task_service.create_task(
        db,
        actor=user,
        project_id=project_id,
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        assignee_id=body.assignee_id,
        due_date=body.due_date,
        label_ids=body.label_ids,
        request=request,
    )
    await db.commit()
    hydrated = await task_service.hydrate_task(db, task=task)
    return _detail_from_hydrated(hydrated)


# ──────────────────────────────────────────────────────────────────────────────
# Task by id
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/tasks/{task_id}", response_model=TaskDetail)
async def read_task(task_id: UUID, db: DbDep, user: UserDep) -> TaskDetail:
    task = await task_service.assert_task_accessible(db, user=user, task_id=task_id)
    hydrated = await task_service.hydrate_task(db, task=task)
    return _detail_from_hydrated(hydrated)


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskDetail,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.EDIT_TASK))],
)
async def update_task_endpoint(
    task_id: UUID,
    body: UpdateTaskRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
) -> TaskDetail:
    task = await task_service.assert_task_accessible(db, user=user, task_id=task_id)
    fields_set = body.model_fields_set
    fields = {k: getattr(body, k) for k in fields_set if k != "label_ids"}
    label_ids_set = "label_ids" in fields_set
    await task_service.update_task(
        db,
        actor=user,
        task=task,
        fields=fields,
        label_ids=body.label_ids,
        label_ids_set=label_ids_set,
        request=request,
    )
    await db.commit()
    hydrated = await task_service.hydrate_task(db, task=task)
    return _detail_from_hydrated(hydrated)


@router.patch(
    "/tasks/{task_id}/status",
    response_model=TaskDetail,
    dependencies=[
        Depends(verify_csrf),
        Depends(require_action(Action.CHANGE_TASK_STATUS)),
    ],
)
async def update_task_status(
    task_id: UUID,
    body: UpdateStatusRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
) -> TaskDetail:
    task = await task_service.assert_task_accessible(db, user=user, task_id=task_id)
    await task_service.change_status(
        db, actor=user, task=task, new_status=body.status, request=request
    )
    await db.commit()
    hydrated = await task_service.hydrate_task(db, task=task)
    return _detail_from_hydrated(hydrated)
