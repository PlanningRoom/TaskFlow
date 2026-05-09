"""Invitation DTOs (PRD §3.3, screen inventory §3.9, §5.4)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr

from taskflow.schemas.members import Role
from taskflow.schemas.users import UserSummary

InvitationStatus = Literal["pending", "accepted", "expired"]


class InvitationDTO(BaseModel):
    id: UUID
    email: str
    role: Role
    status: InvitationStatus
    invited_by: UserSummary | None
    sent_at: datetime
    expires_at: datetime
    accepted_at: datetime | None


class ListInvitationsResponse(BaseModel):
    invitations: list[InvitationDTO]


class SendInvitationRequest(BaseModel):
    email: EmailStr
    role: Role


class SendInvitationResponse(BaseModel):
    invitation: InvitationDTO


class ResendInvitationResponse(BaseModel):
    invitation: InvitationDTO
