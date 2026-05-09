"""Workspace settings service (PRD §4.1)."""

from __future__ import annotations

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.audit import write_audit_log
from taskflow.db.models.user import User
from taskflow.db.models.workspace import Workspace


async def update_workspace(
    db: AsyncSession,
    *,
    workspace: Workspace,
    actor: User,
    name: str,
    request: Request | None = None,
) -> Workspace:
    """Owner/Admin update of the workspace name (PRD §4.1)."""
    workspace.name = name
    await write_audit_log(
        db,
        event_type="workspace.updated",
        actor_id=actor.id,
        target_id=workspace.id,
        request=request,
        metadata={"name": name},
    )
    return workspace
