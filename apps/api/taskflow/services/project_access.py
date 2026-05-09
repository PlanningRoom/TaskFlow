"""Project membership management (PRD §5.2)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Request
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.audit import write_audit_log
from taskflow.db.models.project import Project, ProjectMembership
from taskflow.db.models.user import User
from taskflow.errors import ConflictError, NotFoundError


async def list_project_members(db: AsyncSession, *, project: Project) -> list[User]:
    """All users with explicit access to the project."""
    rows = await db.execute(
        select(User)
        .join(ProjectMembership, ProjectMembership.user_id == User.id)
        .where(ProjectMembership.project_id == project.id)
        .order_by(User.name.asc())
    )
    return list(rows.scalars().all())


async def grant_access(
    db: AsyncSession,
    *,
    actor: User,
    project: Project,
    target_user_id: UUID,
    request: Request | None = None,
) -> User:
    """Add a workspace user to a project's access list."""
    target = await db.scalar(
        select(User).where(
            User.id == target_user_id,
            User.workspace_id == project.workspace_id,
            User.deleted_at.is_(None),
        )
    )
    if target is None:
        raise NotFoundError("User not found.", code="USER_NOT_FOUND")

    existing = await db.scalar(
        select(ProjectMembership).where(
            ProjectMembership.project_id == project.id,
            ProjectMembership.user_id == target.id,
        )
    )
    if existing is not None:
        raise ConflictError(
            "User already has access to this project.",
            code="PROJECT_ACCESS_EXISTS",
        )

    db.add(ProjectMembership(project_id=project.id, user_id=target.id))
    await db.flush()

    await write_audit_log(
        db,
        event_type="project.access.added",
        actor_id=actor.id,
        target_id=project.id,
        request=request,
        metadata={"user_id": str(target.id)},
    )
    return target


async def revoke_access(
    db: AsyncSession,
    *,
    actor: User,
    project: Project,
    target_user_id: UUID,
    request: Request | None = None,
) -> None:
    """Remove a user from a project's access list."""
    membership = await db.scalar(
        select(ProjectMembership).where(
            ProjectMembership.project_id == project.id,
            ProjectMembership.user_id == target_user_id,
        )
    )
    if membership is None:
        raise NotFoundError(
            "User does not have access to this project.",
            code="PROJECT_ACCESS_NOT_FOUND",
        )

    await db.execute(
        delete(ProjectMembership).where(
            ProjectMembership.project_id == project.id,
            ProjectMembership.user_id == target_user_id,
        )
    )
    await write_audit_log(
        db,
        event_type="project.access.removed",
        actor_id=actor.id,
        target_id=project.id,
        request=request,
        metadata={"user_id": str(target_user_id)},
    )
