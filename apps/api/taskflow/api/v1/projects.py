"""Project + project-access endpoints (Phase C2)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from taskflow.auth.dependencies import (
    DbDep,
    UserDep,
    WorkspaceDep,
    require_action,
    require_project_access,
    verify_csrf,
)
from taskflow.auth.permissions import Action
from taskflow.db.models.project import Project
from taskflow.schemas.auth import OkResponse
from taskflow.schemas.projects import (
    CreateProjectRequest,
    GrantProjectAccessRequest,
    GrantProjectAccessResponse,
    ListProjectAccessResponse,
    ListProjectsResponse,
    ProjectDTO,
    ProjectMemberDTO,
    UpdateProjectRequest,
)
from taskflow.schemas.users import user_summary
from taskflow.services import project_access as access_service
from taskflow.services import projects as project_service

router = APIRouter(prefix="/projects", tags=["projects"])


def _project_dto(project: Project) -> ProjectDTO:
    # `created_by` on the model maps to `created_by_id` in the DTO.
    return ProjectDTO(
        id=project.id,
        name=project.name,
        description=project.description,
        color=project.color,
        created_by_id=project.created_by,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=ListProjectsResponse)
async def list_projects(db: DbDep, user: UserDep) -> ListProjectsResponse:
    rows = await project_service.list_visible_projects(db, user=user)
    return ListProjectsResponse(projects=[_project_dto(p) for p in rows])


@router.post(
    "",
    response_model=ProjectDTO,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.CREATE_PROJECT))],
)
async def create_project(
    body: CreateProjectRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
    workspace: WorkspaceDep,
) -> ProjectDTO:
    project = await project_service.create_project(
        db,
        actor=user,
        name=body.name,
        description=body.description,
        color=body.color,
        request=request,
    )
    await db.commit()
    return _project_dto(project)


@router.get(
    "/{project_id}",
    response_model=ProjectDTO,
    dependencies=[Depends(require_project_access())],
)
async def read_project(project_id: UUID, db: DbDep, user: UserDep) -> ProjectDTO:
    project = await project_service.get_project(
        db, workspace_id=user.workspace_id, project_id=project_id
    )
    return _project_dto(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectDTO,
    dependencies=[
        Depends(verify_csrf),
        Depends(require_action(Action.MANAGE_PROJECT_SETTINGS)),
    ],
)
async def update_project(
    project_id: UUID,
    body: UpdateProjectRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
) -> ProjectDTO:
    project = await project_service.update_project(
        db,
        actor=user,
        project_id=project_id,
        name=body.name,
        description=body.description,
        color=body.color,
        request=request,
    )
    await db.commit()
    return _project_dto(project)


# ──────────────────────────────────────────────────────────────────────────────
# Project access
# ──────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{project_id}/access",
    response_model=ListProjectAccessResponse,
    dependencies=[Depends(require_action(Action.MANAGE_PROJECT_ACCESS))],
)
async def list_project_access(
    project_id: UUID, db: DbDep, user: UserDep
) -> ListProjectAccessResponse:
    project = await project_service.get_project(
        db, workspace_id=user.workspace_id, project_id=project_id
    )
    members = await access_service.list_project_members(db, project=project)
    return ListProjectAccessResponse(
        members=[
            ProjectMemberDTO(user=user_summary(m.id, m.name, deleted=m.deleted_at is not None))
            for m in members
        ]
    )


@router.post(
    "/{project_id}/access",
    response_model=GrantProjectAccessResponse,
    dependencies=[
        Depends(verify_csrf),
        Depends(require_action(Action.MANAGE_PROJECT_ACCESS)),
    ],
)
async def grant_project_access(
    project_id: UUID,
    body: GrantProjectAccessRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
) -> GrantProjectAccessResponse:
    project = await project_service.get_project(
        db, workspace_id=user.workspace_id, project_id=project_id
    )
    target = await access_service.grant_access(
        db, actor=user, project=project, target_user_id=body.user_id, request=request
    )
    await db.commit()
    return GrantProjectAccessResponse(
        member=ProjectMemberDTO(
            user=user_summary(target.id, target.name, deleted=target.deleted_at is not None)
        )
    )


@router.delete(
    "/{project_id}/access/{user_id}",
    response_model=OkResponse,
    dependencies=[
        Depends(verify_csrf),
        Depends(require_action(Action.MANAGE_PROJECT_ACCESS)),
    ],
)
async def revoke_project_access(
    project_id: UUID,
    user_id: UUID,
    request: Request,
    db: DbDep,
    user: UserDep,
) -> OkResponse:
    project = await project_service.get_project(
        db, workspace_id=user.workspace_id, project_id=project_id
    )
    await access_service.revoke_access(
        db, actor=user, project=project, target_user_id=user_id, request=request
    )
    await db.commit()
    return OkResponse()
