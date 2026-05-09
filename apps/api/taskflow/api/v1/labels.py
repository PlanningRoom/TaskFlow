"""Label CRUD endpoints (Phase C1)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from taskflow.auth.dependencies import (
    DbDep,
    UserDep,
    WorkspaceDep,
    require_action,
    verify_csrf,
)
from taskflow.auth.permissions import Action
from taskflow.schemas.auth import OkResponse
from taskflow.schemas.labels import (
    CreateLabelRequest,
    LabelDTO,
    ListLabelsResponse,
    UpdateLabelRequest,
)
from taskflow.services import labels as label_service

router = APIRouter(prefix="/labels", tags=["labels"])


@router.get("", response_model=ListLabelsResponse)
async def list_labels(db: DbDep, workspace: WorkspaceDep) -> ListLabelsResponse:
    rows = await label_service.list_labels(db, workspace_id=workspace.id)
    return ListLabelsResponse(labels=[LabelDTO.model_validate(r) for r in rows])


@router.post(
    "",
    response_model=LabelDTO,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.MANAGE_LABELS))],
)
async def create_label(
    body: CreateLabelRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
    workspace: WorkspaceDep,
) -> LabelDTO:
    label = await label_service.create_label(
        db,
        workspace_id=workspace.id,
        actor=user,
        name=body.name,
        color=body.color,
        request=request,
    )
    await db.commit()
    return LabelDTO.model_validate(label)


@router.patch(
    "/{label_id}",
    response_model=LabelDTO,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.MANAGE_LABELS))],
)
async def update_label(
    label_id: UUID,
    body: UpdateLabelRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
    workspace: WorkspaceDep,
) -> LabelDTO:
    label = await label_service.update_label(
        db,
        workspace_id=workspace.id,
        label_id=label_id,
        actor=user,
        name=body.name,
        color=body.color,
        request=request,
    )
    await db.commit()
    return LabelDTO.model_validate(label)


@router.delete(
    "/{label_id}",
    response_model=OkResponse,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.MANAGE_LABELS))],
)
async def delete_label(
    label_id: UUID,
    request: Request,
    db: DbDep,
    user: UserDep,
    workspace: WorkspaceDep,
) -> OkResponse:
    await label_service.delete_label(
        db,
        workspace_id=workspace.id,
        label_id=label_id,
        actor=user,
        request=request,
    )
    await db.commit()
    return OkResponse()
