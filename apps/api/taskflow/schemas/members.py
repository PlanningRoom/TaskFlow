"""Member DTOs (PRD §4.2, screen inventory §3.9)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

Role = Literal["owner", "admin", "member", "viewer"]


class MemberDTO(BaseModel):
    """Flat shape per screen inventory §3.9 — `id`, `display_name`, `email`,
    `initials`, `avatar_color`, `role`. Deleted users are filtered out by the
    list endpoint (anonymization removes the email anyway, so they'd render
    blank). `joined_at` is included for the row's secondary metadata.
    """

    id: UUID
    display_name: str | None
    email: str | None
    initials: str
    avatar_color: str
    role: Role
    joined_at: datetime


class ListMembersResponse(BaseModel):
    members: list[MemberDTO]


class ChangeRoleRequest(BaseModel):
    role: Role
