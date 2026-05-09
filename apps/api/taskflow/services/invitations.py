"""Invitation send/list/resend service (PRD §3.3, ADR 011)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.auth.audit import write_audit_log
from taskflow.auth.tokens import generate_token
from taskflow.db.models.invitation import Invitation
from taskflow.db.models.user import User
from taskflow.errors import ConflictError, NotFoundError
from taskflow.schemas.members import Role

# Invitation lifetime per PRD §3.3 / TDD §11.
INVITATION_TTL_DAYS = 7


async def list_invitations(db: AsyncSession, *, workspace_id: UUID) -> list[Invitation]:
    rows = await db.execute(
        select(Invitation)
        .where(Invitation.workspace_id == workspace_id)
        .order_by(Invitation.created_at.desc())
    )
    return list(rows.scalars().all())


async def send_invitation(
    db: AsyncSession,
    *,
    workspace_id: UUID,
    actor: User,
    email: str,
    role: Role,
    request: Request | None = None,
) -> tuple[Invitation, str]:
    """Create a pending invitation and return (row, raw_token).

    Raises ConflictError if there's already a pending invitation for the email
    in the workspace.
    """
    existing = await db.scalar(
        select(Invitation).where(
            Invitation.workspace_id == workspace_id,
            Invitation.email == email,
            Invitation.accepted_at.is_(None),
            Invitation.expires_at > datetime.now(UTC),
        )
    )
    if existing is not None:
        raise ConflictError(
            "An invitation is already pending for that email.",
            code="INVITATION_PENDING",
        )

    raw, token_hash = generate_token(32)
    invitation = Invitation(
        workspace_id=workspace_id,
        email=email,
        role=role,
        token_hash=token_hash,
        invited_by=actor.id,
        expires_at=datetime.now(UTC) + timedelta(days=INVITATION_TTL_DAYS),
    )
    db.add(invitation)
    await db.flush()

    await write_audit_log(
        db,
        event_type="workspace.invitation.sent",
        actor_id=actor.id,
        target_id=invitation.id,
        request=request,
        metadata={"email": email, "role": role},
    )
    return invitation, raw


async def resend_invitation(
    db: AsyncSession,
    *,
    workspace_id: UUID,
    invitation_id: UUID,
    actor: User,
    request: Request | None = None,
) -> tuple[Invitation, str]:
    """Regenerate the token + extend expiry for a pending invitation."""
    invitation = await db.scalar(
        select(Invitation).where(
            Invitation.id == invitation_id,
            Invitation.workspace_id == workspace_id,
        )
    )
    if invitation is None:
        raise NotFoundError("Invitation not found.", code="INVITATION_NOT_FOUND")
    if invitation.accepted_at is not None:
        raise ConflictError("Invitation has already been accepted.", code="INVITATION_ACCEPTED")

    raw, token_hash = generate_token(32)
    invitation.token_hash = token_hash
    invitation.expires_at = datetime.now(UTC) + timedelta(days=INVITATION_TTL_DAYS)

    await write_audit_log(
        db,
        event_type="workspace.invitation.resent",
        actor_id=actor.id,
        target_id=invitation.id,
        request=request,
    )
    return invitation, raw


def derive_status(invitation: Invitation) -> str:
    if invitation.accepted_at is not None:
        return "accepted"
    if invitation.expires_at <= datetime.now(UTC):
        return "expired"
    return "pending"
