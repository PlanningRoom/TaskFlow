from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from taskflow.db.models import Base, CreatedAtMixin, UUIDPKMixin

# Source of truth: ADR 084. Adding a new event requires a migration that
# extends the CHECK constraint below.
AUDIT_EVENT_TYPES = (
    # Auth + self-service (0001_initial).
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
    # Part C admin events (migration 0002).
    "workspace.updated",
    "workspace.label.created",
    "workspace.label.updated",
    "workspace.label.deleted",
    "project.created",
    "project.updated",
    "project.access.added",
    "project.access.removed",
)

_EVENT_TYPE_CHECK_SQL = "event_type IN (" + ", ".join(f"'{e}'" for e in AUDIT_EVENT_TYPES) + ")"


class AuditLog(UUIDPKMixin, CreatedAtMixin, Base):
    """Append-only audit log (ADR 084)."""

    __tablename__ = "audit_log"
    __table_args__ = (
        CheckConstraint(_EVENT_TYPE_CHECK_SQL, name="ck_audit_log_event_type_in_enum"),
        Index("ix_audit_log_created_at", "created_at"),
    )

    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    target_id: Mapped[UUID | None] = mapped_column(nullable=True)
    ip: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
