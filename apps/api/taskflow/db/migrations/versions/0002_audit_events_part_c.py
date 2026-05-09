"""extend audit_log event types for Part C admin events

Revision ID: 0002_audit_events_part_c
Revises: 0001_initial
Create Date: 2026-05-09

Extends the `audit_log.event_type` CHECK constraint with the eight new admin
events emitted by Part C (workspace settings update, label CRUD, project CRUD,
project access add/remove). Task and comment changes deliberately stay out of
the audit_log per ADR 084's scope (security-sensitive admin actions only) —
they live in `activity_events` per ADR 063 instead.

Source of truth for the canonical list: ADR 084.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0002_audit_events_part_c"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

AUDIT_EVENT_TYPES_V2 = (
    # Existing (0001_initial).
    "auth.signup",
    "auth.login.success",
    "auth.login.failure",
    "auth.logout",
    "auth.password_reset.requested",
    "auth.password_reset.completed",
    "auth.password_changed",
    "auth.profile.updated",
    "workspace.user.role_changed",
    "workspace.user.removed",
    "workspace.invitation.sent",
    "workspace.invitation.resent",
    "workspace.invitation.accepted",
    "account.deleted",
    # New in 0002 (Part C admin events).
    "workspace.updated",
    "workspace.label.created",
    "workspace.label.updated",
    "workspace.label.deleted",
    "project.created",
    "project.updated",
    "project.access.added",
    "project.access.removed",
)
AUDIT_EVENT_CHECK_V2 = "event_type IN (" + ", ".join(f"'{e}'" for e in AUDIT_EVENT_TYPES_V2) + ")"

AUDIT_EVENT_TYPES_V1 = (
    "auth.signup",
    "auth.login.success",
    "auth.login.failure",
    "auth.logout",
    "auth.password_reset.requested",
    "auth.password_reset.completed",
    "auth.password_changed",
    "auth.profile.updated",
    "workspace.user.role_changed",
    "workspace.user.removed",
    "workspace.invitation.sent",
    "workspace.invitation.resent",
    "workspace.invitation.accepted",
    "account.deleted",
)
AUDIT_EVENT_CHECK_V1 = "event_type IN (" + ", ".join(f"'{e}'" for e in AUDIT_EVENT_TYPES_V1) + ")"


def upgrade() -> None:
    op.drop_constraint("ck_audit_log_event_type_in_enum", "audit_log", type_="check")
    op.create_check_constraint(
        "ck_audit_log_event_type_in_enum",
        "audit_log",
        AUDIT_EVENT_CHECK_V2,
    )


def downgrade() -> None:
    op.drop_constraint("ck_audit_log_event_type_in_enum", "audit_log", type_="check")
    op.create_check_constraint(
        "ck_audit_log_event_type_in_enum",
        "audit_log",
        AUDIT_EVENT_CHECK_V1,
    )
