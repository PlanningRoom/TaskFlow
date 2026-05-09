"""Activity feed endpoints (Phase C5, ADR 063)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select

from taskflow.auth.dependencies import DbDep, UserDep
from taskflow.db.models.activity_event import ActivityEvent
from taskflow.db.models.project import Project
from taskflow.db.models.user import User
from taskflow.schemas.activity import ActivityEventDTO, ListActivityResponse
from taskflow.schemas.tasks import ProjectRefDTO
from taskflow.schemas.users import user_summary
from taskflow.services import activity as activity_service
from taskflow.services.projects import assert_project_visible

router = APIRouter(prefix="/activity", tags=["activity"])


async def _hydrate_dto(db: DbDep, event: ActivityEvent) -> ActivityEventDTO:
    actor_obj: User | None = None
    if event.actor_id is not None:
        actor_obj = await db.scalar(select(User).where(User.id == event.actor_id))
    project_ref = None
    if event.project_id is not None:
        project = await db.scalar(select(Project).where(Project.id == event.project_id))
        if project is not None:
            project_ref = ProjectRefDTO(id=project.id, name=project.name)

    return ActivityEventDTO(
        id=event.id,
        event_type=event.event_type,
        actor=user_summary(actor_obj.id, actor_obj.name, deleted=actor_obj.deleted_at is not None)
        if actor_obj is not None
        else None,
        subject_type=event.subject_type,
        subject_id=event.subject_id,
        project=project_ref,
        metadata=event.metadata_,
        created_at=event.created_at,
    )


@router.get("", response_model=ListActivityResponse)
async def list_activity(
    db: DbDep,
    user: UserDep,
    project_id: UUID | None = None,
    cursor: str | None = None,
    limit: int = activity_service.DEFAULT_LIMIT,
) -> ListActivityResponse:
    if project_id is not None:
        # Project scope — gate via assert_project_visible (404 if cross-workspace,
        # 403 if no access).
        await assert_project_visible(db, user=user, project_id=project_id)

    rows, next_cursor = await activity_service.list_activity(
        db, user=user, project_id=project_id, cursor=cursor, limit=limit
    )
    events = [await _hydrate_dto(db, e) for e in rows]
    return ListActivityResponse(events=events, next_cursor=next_cursor)
