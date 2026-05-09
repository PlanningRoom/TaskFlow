"""Member DTOs (PRD §4.2, screen inventory §3.9)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from taskflow.schemas.users import UserSummary

Role = Literal["owner", "admin", "member", "viewer"]
MemberStatus = Literal["active", "deleted"]


class MemberDTO(BaseModel):
    user: UserSummary
    email: str | None
    role: Role
    status: MemberStatus
    joined_at: datetime


class ListMembersResponse(BaseModel):
    members: list[MemberDTO]


class ChangeRoleRequest(BaseModel):
    role: Role
