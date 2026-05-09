"""Member admin service (PRD §4.2, ADR 065)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Request
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.audit import write_audit_log
from taskflow.db.models.project import ProjectMembership
from taskflow.db.models.user import User
from taskflow.errors import ConflictError, NotFoundError
from taskflow.schemas.members import Role
from taskflow.services.users import anonymize_user


async def list_members(db: AsyncSession, *, workspace_id: UUID) -> list[User]:
    """Return all users (active and anonymized) in the workspace."""
    rows = await db.execute(
        select(User).where(User.workspace_id == workspace_id).order_by(User.created_at.asc())
    )
    return list(rows.scalars().all())


async def _load_target(db: AsyncSession, *, workspace_id: UUID, user_id: UUID) -> User:
    target = await db.scalar(
        select(User).where(User.id == user_id, User.workspace_id == workspace_id)
    )
    if target is None:
        raise NotFoundError("Member not found.", code="MEMBER_NOT_FOUND")
    return target


async def change_role(
    db: AsyncSession,
    *,
    workspace_id: UUID,
    target_user_id: UUID,
    new_role: Role,
    actor: User,
    request: Request | None = None,
) -> User:
    """Change a workspace member's role (PRD §2.1, §4.2)."""
    target = await _load_target(db, workspace_id=workspace_id, user_id=target_user_id)
    if target.deleted_at is not None:
        raise NotFoundError("Member not found.", code="MEMBER_NOT_FOUND")
    if target.id == actor.id and new_role != actor.role:
        # Don't let an Owner accidentally demote themselves and lose Owner-only powers.
        # The UI offers a transfer-ownership flow separately; not implemented in v1.
        raise ConflictError("You cannot change your own role.", code="SELF_ROLE_CHANGE_FORBIDDEN")

    previous = target.role
    target.role = new_role

    await write_audit_log(
        db,
        event_type="workspace.user.role_changed",
        actor_id=actor.id,
        target_id=target.id,
        request=request,
        metadata={"from": previous, "to": new_role},
    )
    return target


async def remove_member(
    db: AsyncSession,
    *,
    workspace_id: UUID,
    target_user_id: UUID,
    actor: User,
    request: Request | None = None,
) -> User:
    """Owner-only member removal (PRD §4.2, ADR 065).

    Anonymizes the user in place, drops their sessions, unassigns tasks,
    deletes their project memberships. Audit row written.
    """
    target = await _load_target(db, workspace_id=workspace_id, user_id=target_user_id)
    if target.id == actor.id:
        raise ConflictError("You cannot remove yourself.", code="SELF_REMOVE_FORBIDDEN")
    if target.deleted_at is not None:
        # Idempotent: already anonymized. Don't re-write audit row.
        return target

    await anonymize_user(db, target)
    await db.execute(delete(ProjectMembership).where(ProjectMembership.user_id == target.id))
    await write_audit_log(
        db,
        event_type="workspace.user.removed",
        actor_id=actor.id,
        target_id=target.id,
        request=request,
    )
    return target
