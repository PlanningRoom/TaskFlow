"""Shared enum-like constants.

Centralised so the seed script, services, and tests can reference the same
canonical lists. The DB CHECK constraints in `taskflow/db/models/*` enforce
the same strings; Alembic migrations are authoritative for the schema.
"""

from __future__ import annotations

USER_ROLES: tuple[str, ...] = ("owner", "admin", "member", "viewer")
TASK_STATUSES: tuple[str, ...] = (
    "backlog",
    "todo",
    "in_progress",
    "in_review",
    "done",
    "cancelled",
)
TASK_PRIORITIES: tuple[str, ...] = ("none", "low", "medium", "high", "urgent")
LABEL_COLORS: tuple[str, ...] = (
    "blue",
    "green",
    "red",
    "purple",
    "amber",
    "pink",
    "cyan",
    "orange",
)
