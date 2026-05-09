"""Project CRUD service (PRD §5, ADR 003)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.audit import write_audit_log
from taskflow.auth.permissions import has_implicit_project_access
from taskflow.db.models.project import Project, ProjectMembership
from taskflow.db.models.user import User
from taskflow.errors import NotFoundError, PermissionDeniedError


async def list_visible_projects(db: AsyncSession, *, user: User) -> list[Project]:
    """Projects the caller can see in their workspace.

    Owner/Admin see all workspace projects (implicit access).
    Member/Viewer see only projects with an explicit membership row.
    """
    if has_implicit_project_access(user.role):
        rows = await db.execute(
            select(Project)
            .where(Project.workspace_id == user.workspace_id)
            .order_by(Project.name.asc())
        )
        return list(rows.scalars().all())

    rows = await db.execute(
        select(Project)
        .join(ProjectMembership, ProjectMembership.project_id == Project.id)
        .where(
            Project.workspace_id == user.workspace_id,
            ProjectMembership.user_id == user.id,
        )
        .order_by(Project.name.asc())
    )
    return list(rows.scalars().all())


async def get_project(db: AsyncSession, *, workspace_id: UUID, project_id: UUID) -> Project:
    """Fetch a project scoped to the workspace. 404 on miss or cross-workspace."""
    project = await db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.workspace_id == workspace_id,
        )
    )
    if project is None:
        raise NotFoundError("Project not found.", code="PROJECT_NOT_FOUND")
    return project


async def assert_project_visible(db: AsyncSession, *, user: User, project_id: UUID) -> Project:
    """Single source of truth for project access (TDD §11.5).

    Returns the project (loaded as a side effect) so callers can avoid a
    second query.
    """
    project = await get_project(db, workspace_id=user.workspace_id, project_id=project_id)
    if has_implicit_project_access(user.role):
        return project
    membership = await db.scalar(
        select(ProjectMembership).where(
            ProjectMembership.project_id == project_id,
            ProjectMembership.user_id == user.id,
        )
    )
    if membership is None:
        raise PermissionDeniedError(
            "You don't have access to this project.", code="PROJECT_ACCESS_DENIED"
        )
    return project


async def create_project(
    db: AsyncSession,
    *,
    actor: User,
    name: str,
    description: str | None,
    color: str | None,
    request: Request | None = None,
) -> Project:
    project = Project(
        workspace_id=actor.workspace_id,
        name=name,
        description=description,
        color=color,
        created_by=actor.id,
    )
    db.add(project)
    await db.flush()

    # Auto-grant the creator project access if they don't have implicit access
    # (Member-creator). Owner/Admin see every project anyway.
    if not has_implicit_project_access(actor.role):
        db.add(ProjectMembership(project_id=project.id, user_id=actor.id))
        await db.flush()

    await write_audit_log(
        db,
        event_type="project.created",
        actor_id=actor.id,
        target_id=project.id,
        request=request,
        metadata={"name": name},
    )
    return project


async def update_project(
    db: AsyncSession,
    *,
    actor: User,
    project_id: UUID,
    name: str | None,
    description: str | None,
    color: str | None,
    request: Request | None = None,
) -> Project:
    project = await get_project(db, workspace_id=actor.workspace_id, project_id=project_id)
    changed: dict[str, str | None] = {}
    if name is not None and name != project.name:
        project.name = name
        changed["name"] = name
    if description is not None and description != project.description:
        project.description = description
        changed["description"] = description
    if color is not None and color != project.color:
        project.color = color
        changed["color"] = color

    await write_audit_log(
        db,
        event_type="project.updated",
        actor_id=actor.id,
        target_id=project.id,
        request=request,
        metadata=changed,
    )
    return project
