"""Server-side @mention parser (TDD §6.6).

Resolves `@token` references in comment bodies against workspace members.
Unknown handles drop. Cross-workspace users are not findable. Used by both
the comment service (DTO carries resolved mentions) and the notification
service (dispatch on mention).
"""

from __future__ import annotations

import re
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.user import User

# Match `@<token>` where the token contains letters / digits / `_` / `-`.
# Word boundary at the start (no `@` mid-email — the regex won't match
# `user@example.com` because `r` is not a whitespace boundary).
_MENTION_RE = re.compile(r"(?:^|(?<=\s))@([A-Za-z0-9_-]+)")


def extract_handles(body: str) -> list[str]:
    """Return the handles (without `@`) in the order they appear, de-duped."""
    seen: dict[str, None] = {}
    for match in _MENTION_RE.finditer(body):
        handle = match.group(1).lower()
        if handle and handle not in seen:
            seen[handle] = None
    return list(seen.keys())


def _normalize_name(name: str | None) -> str:
    if not name:
        return ""
    return name.replace(" ", "-").lower()


async def resolve_mentions(db: AsyncSession, *, body: str, workspace_id: UUID) -> list[User]:
    """Resolve handles to live workspace users.

    Matching is case-insensitive: `@aurora-owner` matches User.name "Aurora
    Owner" (spaces → hyphens). Returns users in the order their handles first
    appear in the body. Drops unknown handles.
    """
    handles = extract_handles(body)
    if not handles:
        return []

    rows = await db.execute(
        select(User).where(
            User.workspace_id == workspace_id,
            User.deleted_at.is_(None),
            func.replace(func.lower(User.name), " ", "-").in_(handles),
        )
    )
    by_handle: dict[str, User] = {}
    for user in rows.scalars().all():
        by_handle[_normalize_name(user.name)] = user

    resolved: list[User] = []
    seen_ids: set[UUID] = set()
    for handle in handles:
        match = by_handle.get(handle)
        if match is not None and match.id not in seen_ids:
            resolved.append(match)
            seen_ids.add(match.id)
    return resolved
