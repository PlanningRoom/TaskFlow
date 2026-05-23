"""Workspace, member, and invitation endpoints (Phase C1)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy import select

from taskflow.auth.dependencies import (
    DbDep,
    UserDep,
    WorkspaceDep,
    require_action,
    verify_csrf,
)
from taskflow.auth.permissions import Action
from taskflow.db.models.invitation import Invitation
from taskflow.db.models.user import User
from taskflow.rate_limit import limiter, workspace_key
from taskflow.schemas.auth import OkResponse
from taskflow.schemas.invitations import (
    InvitationDTO,
    ListInvitationsResponse,
    ResendInvitationResponse,
    SendInvitationRequest,
    SendInvitationResponse,
)
from taskflow.schemas.members import (
    ChangeRoleRequest,
    ListMembersResponse,
    MemberDTO,
)
from taskflow.schemas.users import avatar_color_for, initials_from, user_summary
from taskflow.schemas.workspaces import UpdateWorkspaceRequest, WorkspaceDTO
from taskflow.services import invitations as invitation_service
from taskflow.services import members as member_service
from taskflow.services import workspaces as workspace_service
from taskflow.settings import settings

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


# ──────────────────────────────────────────────────────────────────────────────
# Workspace details
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/me", response_model=WorkspaceDTO)
async def read_workspace(workspace: WorkspaceDep) -> WorkspaceDTO:
    return WorkspaceDTO.model_validate(workspace)


@router.patch(
    "/me",
    response_model=WorkspaceDTO,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.UPDATE_WORKSPACE))],
)
async def update_workspace(
    body: UpdateWorkspaceRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
    workspace: WorkspaceDep,
) -> WorkspaceDTO:
    await workspace_service.update_workspace(
        db, workspace=workspace, actor=user, name=body.name, request=request
    )
    await db.commit()
    return WorkspaceDTO.model_validate(workspace)


# ──────────────────────────────────────────────────────────────────────────────
# Members
# ──────────────────────────────────────────────────────────────────────────────


def _member_dto(user: User) -> MemberDTO:
    return MemberDTO(
        id=user.id,
        display_name=user.name,
        email=user.email,
        initials=initials_from(user.name),
        avatar_color=avatar_color_for(user.id),
        role=user.role,
        joined_at=user.created_at,
    )


@router.get(
    "/me/members",
    response_model=ListMembersResponse,
    dependencies=[Depends(require_action(Action.UPDATE_WORKSPACE))],
)
async def list_members(db: DbDep, workspace: WorkspaceDep) -> ListMembersResponse:
    rows = await member_service.list_members(db, workspace_id=workspace.id)
    return ListMembersResponse(members=[_member_dto(u) for u in rows])


@router.patch(
    "/me/members/{user_id}",
    response_model=MemberDTO,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.CHANGE_USER_ROLES))],
)
async def change_member_role(
    user_id: UUID,
    body: ChangeRoleRequest,
    request: Request,
    db: DbDep,
    user: UserDep,
    workspace: WorkspaceDep,
) -> MemberDTO:
    target = await member_service.change_role(
        db,
        workspace_id=workspace.id,
        target_user_id=user_id,
        new_role=body.role,
        actor=user,
        request=request,
    )
    await db.commit()
    return _member_dto(target)


@router.delete(
    "/me/members/{user_id}",
    response_model=OkResponse,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.REMOVE_USERS))],
)
async def remove_member(
    user_id: UUID,
    request: Request,
    db: DbDep,
    user: UserDep,
    workspace: WorkspaceDep,
) -> OkResponse:
    await member_service.remove_member(
        db,
        workspace_id=workspace.id,
        target_user_id=user_id,
        actor=user,
        request=request,
    )
    await db.commit()
    return OkResponse()


# ──────────────────────────────────────────────────────────────────────────────
# Invitations
# ──────────────────────────────────────────────────────────────────────────────


def _dispatch_invitation_email(email: str, raw_token: str) -> None:
    """Placeholder — replaced by the SES/MailHog adapter in Phase D2."""
    _ = (email, raw_token)


def _invitation_dto(invitation: Invitation, inviter: User | None) -> InvitationDTO:
    return InvitationDTO(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role,
        status=invitation_service.derive_status(invitation),
        invited_by=user_summary(inviter.id, inviter.name, deleted=inviter.deleted_at is not None)
        if inviter is not None
        else None,
        sent_at=invitation.created_at,
        expires_at=invitation.expires_at,
        accepted_at=invitation.accepted_at,
    )


async def _resolve_inviters(db: DbDep, invitations: list[Invitation]) -> dict[UUID, User]:
    if not invitations:
        return {}
    ids = {inv.invited_by for inv in invitations}
    rows = await db.execute(select(User).where(User.id.in_(ids)))
    return {u.id: u for u in rows.scalars().all()}


@router.get(
    "/me/invitations",
    response_model=ListInvitationsResponse,
    dependencies=[Depends(require_action(Action.INVITE_USERS))],
)
async def list_invitations(db: DbDep, workspace: WorkspaceDep) -> ListInvitationsResponse:
    rows = await invitation_service.list_invitations(db, workspace_id=workspace.id)
    inviters = await _resolve_inviters(db, rows)
    return ListInvitationsResponse(
        invitations=[_invitation_dto(r, inviters.get(r.invited_by)) for r in rows]
    )


@router.post(
    "/me/invitations",
    response_model=SendInvitationResponse,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.INVITE_USERS))],
)
@limiter.limit(settings.rate_limit_invites_per_workspace, key_func=workspace_key)
async def send_invitation(
    body: SendInvitationRequest,
    request: Request,
    background: BackgroundTasks,
    db: DbDep,
    user: UserDep,
    workspace: WorkspaceDep,
) -> SendInvitationResponse:
    invitation, raw_token = await invitation_service.send_invitation(
        db,
        workspace_id=workspace.id,
        actor=user,
        email=body.email,
        role=body.role,
        request=request,
    )
    await db.commit()
    background.add_task(_dispatch_invitation_email, body.email, raw_token)
    return SendInvitationResponse(invitation=_invitation_dto(invitation, user))


@router.post(
    "/me/invitations/{invitation_id}/resend",
    response_model=ResendInvitationResponse,
    dependencies=[Depends(verify_csrf), Depends(require_action(Action.INVITE_USERS))],
)
async def resend_invitation(
    invitation_id: UUID,
    request: Request,
    background: BackgroundTasks,
    db: DbDep,
    user: UserDep,
    workspace: WorkspaceDep,
) -> ResendInvitationResponse:
    invitation, raw_token = await invitation_service.resend_invitation(
        db,
        workspace_id=workspace.id,
        invitation_id=invitation_id,
        actor=user,
        request=request,
    )
    await db.commit()
    background.add_task(_dispatch_invitation_email, invitation.email, raw_token)

    inviter = (await _resolve_inviters(db, [invitation])).get(invitation.invited_by)
    return ResendInvitationResponse(invitation=_invitation_dto(invitation, inviter))
