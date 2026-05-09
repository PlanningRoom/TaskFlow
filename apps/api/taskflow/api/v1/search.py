"""Search endpoint (Phase C7, ADR 062)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from taskflow.auth.dependencies import DbDep, UserDep, require_action
from taskflow.auth.permissions import Action
from taskflow.schemas.search import SearchResponse, SearchResult
from taskflow.schemas.tasks import ProjectRefDTO
from taskflow.services import search as search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get(
    "",
    response_model=SearchResponse,
    dependencies=[Depends(require_action(Action.SEARCH))],
)
async def search_endpoint(
    db: DbDep,
    user: UserDep,
    q: str = "",
    include_cancelled: bool = False,
) -> SearchResponse:
    pairs = await search_service.search_tasks(
        db, user=user, query=q, include_cancelled=include_cancelled
    )
    return SearchResponse(
        results=[
            SearchResult(
                task_id=task.id,
                title=task.title,
                status=task.status,
                project=ProjectRefDTO(id=project.id, name=project.name),
            )
            for task, project in pairs
        ]
    )
