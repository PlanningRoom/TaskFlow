"""Shared user DTOs (screen inventory §8 / TDD §9.4)."""

from __future__ import annotations

import hashlib
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# DRD §2.10 deterministic avatar palette (six colors).
_AVATAR_PALETTE = (
    "indigo",
    "violet",
    "amber",
    "emerald",
    "rose",
    "sky",
)


def initials_from(name: str | None, fallback: str = "?") -> str:
    """Return up to two upper-case initials from a name."""
    if not name:
        return fallback
    parts = [p for p in name.split() if p]
    if not parts:
        return fallback
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][:1] + parts[-1][:1]).upper()


def avatar_color_for(user_id: UUID) -> str:
    """Map a user id to one of the six DRD §2.10 colors deterministically."""
    digest = hashlib.sha256(user_id.bytes).digest()
    return _AVATAR_PALETTE[digest[0] % len(_AVATAR_PALETTE)]


class UserSummary(BaseModel):
    """Lightweight user reference used in listings, mentions, assignments."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str | None = Field(default=None)
    initials: str
    avatar_color: str
    deleted: bool = False


class CurrentUser(BaseModel):
    """Self-DTO for `/auth/me` and the response of auth mutations."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str | None
    role: str
    workspace_id: UUID
    initials: str
    avatar_color: str


def user_summary(user_id: UUID, name: str | None, deleted: bool = False) -> UserSummary:
    return UserSummary(
        id=user_id,
        display_name=None if deleted else name,
        initials=initials_from(name) if not deleted else "?",
        avatar_color=avatar_color_for(user_id),
        deleted=deleted,
    )


def current_user_dto(
    *, user_id: UUID, email: str, name: str | None, role: str, workspace_id: UUID
) -> CurrentUser:
    return CurrentUser(
        id=user_id,
        email=email,
        display_name=name,
        role=role,
        workspace_id=workspace_id,
        initials=initials_from(name, fallback=email[:1].upper() if email else "?"),
        avatar_color=avatar_color_for(user_id),
    )
