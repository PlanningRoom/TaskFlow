"""Comment endpoints (Phase C4, ADR 088)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from taskflow.auth.dependencies import (
    DbDep,
    UserDep,
    require_action,
    verify_csrf,
)
from taskflow.auth.permissions import Action
from taskflow.db.models.comment import Comment
from taskflow.db.models.user import User
from taskflow.schemas.auth import OkResponse
from taskflow.schemas.comments import (
    CommentDTO,
    CreateCommentRequest,
    ListCommentsResponse,
    UpdateCommentRequest,
)
from taskflow.schemas.users import user_summary
from taskflow.services import comments as comment_service

router = APIRouter(tags=["comments"])


def _comment_dto(comment: Comment, author: User | None, mentions: list[User]) -> CommentDTO:
    return CommentDTO(
        id=comment.id,
        body=comment.body,
        author=user_summary(author.id, author.name, deleted=author.deleted_at is not None)
        if author is not None
        else None,
        mentions=[user_summary(u.id, u.name, deleted=u.deleted_at is not None) for u in mentions],
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.get("/tasks/{task_id}/comments", response_model=ListCommentsResponse)
async def list_comments(task_id: UUID, db: DbDep, user: UserDep) -> ListCommentsResponse:
    rows, mentions_by_id = await comment_service.list_task_comments(db, user=user, task_id=task_id)
    # Bulk-load authors.
    from sqlalchemy import select

    author_ids = {c.author_id for c in rows if c.author_id is not None}
    authors: dict[UUID, User] = {}
    if author_ids:
        result = await db.execute(select(User).where(User.id.in_(author_ids)))
        for u in result.scalars().all():
            authors[u.id] = u

    return ListCommentsResponse(
        comments=[
            _comment_dto(c, authors.get(c.author_id) if c.author_id else None, mentions_by_id[c.id])
            for c in rows
        ]
    )


@router.post(
    "/tasks/{task_id}/comments",
    response_model=CommentDTO,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.ADD_COMMENT))],
)
async def create_comment(
    task_id: UUID,
    body: CreateCommentRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
) -> CommentDTO:
    comment, mentions, _task = await comment_service.create_comment(
        db, actor=user, task_id=task_id, body=body.body, request=request
    )
    await db.commit()
    return _comment_dto(comment, user, mentions)


@router.patch(
    "/comments/{comment_id}",
    response_model=CommentDTO,
    dependencies=[Depends(verify_csrf)],
)
async def update_comment_endpoint(
    comment_id: UUID,
    body: UpdateCommentRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
) -> CommentDTO:
    comment, mentions, _task = await comment_service.update_comment(
        db, actor=user, comment_id=comment_id, body=body.body, request=request
    )
    await db.commit()
    # Author is the caller (ADR 088).
    return _comment_dto(comment, user, mentions)


@router.delete(
    "/comments/{comment_id}",
    response_model=OkResponse,
    dependencies=[Depends(verify_csrf)],
)
async def delete_comment_endpoint(
    comment_id: UUID,
    request: Request,
    db: DbDep,
    user: UserDep,
) -> OkResponse:
    await comment_service.delete_comment(db, actor=user, comment_id=comment_id, request=request)
    await db.commit()
    return OkResponse()
