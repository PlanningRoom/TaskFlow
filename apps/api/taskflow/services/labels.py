"""Label CRUD service (PRD §7, DRD §2.9)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.audit import write_audit_log
from taskflow.db.models.label import Label
from taskflow.db.models.user import User
from taskflow.errors import ConflictError, NotFoundError


async def list_labels(db: AsyncSession, *, workspace_id: UUID) -> list[Label]:
    rows = await db.execute(
        select(Label).where(Label.workspace_id == workspace_id).order_by(Label.name.asc())
    )
    return list(rows.scalars().all())


async def _load_label(db: AsyncSession, *, workspace_id: UUID, label_id: UUID) -> Label:
    label = await db.scalar(
        select(Label).where(Label.id == label_id, Label.workspace_id == workspace_id)
    )
    if label is None:
        raise NotFoundError("Label not found.", code="LABEL_NOT_FOUND")
    return label


async def create_label(
    db: AsyncSession,
    *,
    workspace_id: UUID,
    actor: User,
    name: str,
    color: str,
    request: Request | None = None,
) -> Label:
    existing = await db.scalar(
        select(Label).where(Label.workspace_id == workspace_id, Label.name == name)
    )
    if existing is not None:
        raise ConflictError("A label with that name already exists.", code="LABEL_NAME_TAKEN")

    label = Label(workspace_id=workspace_id, name=name, color=color)
    db.add(label)
    await db.flush()
    await write_audit_log(
        db,
        event_type="workspace.label.created",
        actor_id=actor.id,
        target_id=label.id,
        request=request,
        metadata={"name": name, "color": color},
    )
    return label


async def update_label(
    db: AsyncSession,
    *,
    workspace_id: UUID,
    label_id: UUID,
    actor: User,
    name: str | None,
    color: str | None,
    request: Request | None = None,
) -> Label:
    label = await _load_label(db, workspace_id=workspace_id, label_id=label_id)
    if name is not None and name != label.name:
        clash = await db.scalar(
            select(Label).where(
                Label.workspace_id == workspace_id,
                Label.name == name,
                Label.id != label_id,
            )
        )
        if clash is not None:
            raise ConflictError("A label with that name already exists.", code="LABEL_NAME_TAKEN")
        label.name = name
    if color is not None:
        label.color = color
    await write_audit_log(
        db,
        event_type="workspace.label.updated",
        actor_id=actor.id,
        target_id=label.id,
        request=request,
        metadata={"name": label.name, "color": label.color},
    )
    return label


async def delete_label(
    db: AsyncSession,
    *,
    workspace_id: UUID,
    label_id: UUID,
    actor: User,
    request: Request | None = None,
) -> None:
    label = await _load_label(db, workspace_id=workspace_id, label_id=label_id)
    await db.delete(label)
    # task_labels rows cascade via FK ondelete=CASCADE.
    await write_audit_log(
        db,
        event_type="workspace.label.deleted",
        actor_id=actor.id,
        target_id=label_id,
        request=request,
    )
