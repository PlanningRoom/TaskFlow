from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from taskflow.db.models import Base, CreatedAtMixin, UUIDPKMixin

ACTIVITY_EVENT_TYPES = (
    "task.created",
    "task.status_changed",
    "task.assigned",
    "task.unassigned",
    "comment.created",
)


class ActivityEvent(UUIDPKMixin, CreatedAtMixin, Base):
    """Append-only activity feed (ADR 063)."""

    __tablename__ = "activity_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('task.created', 'task.status_changed', 'task.assigned', "
            "'task.unassigned', 'comment.created')",
            name="activity_events_event_type_in_enum",
        ),
        Index("ix_activity_events_workspace_id_created_at", "workspace_id", "created_at"),
        Index("ix_activity_events_project_id_created_at", "project_id", "created_at"),
        Index("ix_activity_events_actor_id_created_at", "actor_id", "created_at"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )
    # No ondelete on actor_id (history-bearing FK; ADR 065).
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    subject_type: Mapped[str] = mapped_column(Text, nullable=False)
    subject_id: Mapped[UUID] = mapped_column(nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
