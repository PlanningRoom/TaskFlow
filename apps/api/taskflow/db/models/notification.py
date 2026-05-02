from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from taskflow.db.models import Base, CreatedAtMixin, UUIDPKMixin

NOTIFICATION_EVENT_TYPES = (
    "mention",
    "task_assigned",
    "task_status_changed",
    "task_commented",
)


class Notification(UUIDPKMixin, CreatedAtMixin, Base):
    """Per-user notification (ADR 064)."""

    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('mention', 'task_assigned', 'task_status_changed', 'task_commented')",
            name="notifications_event_type_in_enum",
        ),
        Index("ix_notifications_recipient_id_created_at", "recipient_id", "created_at"),
        # Partial index for the unread-badge query (TDD §17.1).
        Index(
            "ix_notifications_recipient_id_unread",
            "recipient_id",
            postgresql_where=text("read_at IS NULL"),
        ),
    )

    recipient_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # No ondelete on actor_id (history-bearing FK; ADR 065).
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    task_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True
    )
    project_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
