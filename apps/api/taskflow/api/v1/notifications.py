"""Notification endpoints (Phase C6, ADR 064/070)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select

from taskflow.auth.dependencies import DbDep, UserDep, verify_csrf
from taskflow.db.models.notification import Notification
from taskflow.db.models.project import Project
from taskflow.db.models.task import Task
from taskflow.db.models.user import User
from taskflow.schemas.auth import OkResponse
from taskflow.schemas.notifications import (
    ListNotificationsResponse,
    NotificationDTO,
    NotificationTaskRefDTO,
    UnreadCountResponse,
)
from taskflow.schemas.tasks import ProjectRefDTO
from taskflow.schemas.users import user_summary
from taskflow.services import notifications as notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


async def _hydrate(db: DbDep, n: Notification) -> NotificationDTO:
    actor_obj: User | None = None
    if n.actor_id is not None:
        actor_obj = await db.scalar(select(User).where(User.id == n.actor_id))
    task_ref: NotificationTaskRefDTO | None = None
    if n.task_id is not None:
        task = await db.scalar(select(Task).where(Task.id == n.task_id))
        if task is not None:
            project = await db.scalar(select(Project).where(Project.id == task.project_id))
            if project is not None:
                task_ref = NotificationTaskRefDTO(
                    id=task.id,
                    title=task.title,
                    project=ProjectRefDTO(id=project.id, name=project.name),
                )
    return NotificationDTO(
        id=n.id,
        event_type=n.event_type,
        actor=user_summary(actor_obj.id, actor_obj.name, deleted=actor_obj.deleted_at is not None)
        if actor_obj is not None
        else None,
        task=task_ref,
        metadata=n.metadata_,
        created_at=n.created_at,
        read_at=n.read_at,
    )


@router.get("", response_model=ListNotificationsResponse)
async def list_notifications_endpoint(
    db: DbDep,
    user: UserDep,
    cursor: str | None = None,
    limit: int = notification_service.DEFAULT_LIMIT,
) -> ListNotificationsResponse:
    rows, next_cursor = await notification_service.list_notifications(
        db, user=user, cursor=cursor, limit=limit
    )
    return ListNotificationsResponse(
        notifications=[await _hydrate(db, n) for n in rows], next_cursor=next_cursor
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count_endpoint(db: DbDep, user: UserDep) -> UnreadCountResponse:
    count = await notification_service.unread_count(db, user=user)
    return UnreadCountResponse(count=count)


@router.post(
    "/mark-all-read",
    response_model=OkResponse,
    dependencies=[Depends(verify_csrf)],
)
async def mark_all_read_endpoint(db: DbDep, user: UserDep, request: Request) -> OkResponse:
    await notification_service.mark_all_read(db, user=user)
    await db.commit()
    return OkResponse()


@router.post(
    "/{notification_id}/read",
    response_model=NotificationDTO,
    dependencies=[Depends(verify_csrf)],
)
async def mark_one_read_endpoint(
    notification_id: UUID,
    db: DbDep,
    user: UserDep,
    request: Request,
) -> NotificationDTO:
    row = await notification_service.mark_read(db, user=user, notification_id=notification_id)
    await db.commit()
    return await _hydrate(db, row)
