from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import CheckConstraint, Computed, Date, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from taskflow.db.models import Base, TimestampsMixin, UUIDPKMixin

TASK_STATUSES = ("backlog", "todo", "in_progress", "in_review", "done", "cancelled")
TASK_PRIORITIES = ("none", "low", "medium", "high", "urgent")


class Task(UUIDPKMixin, TimestampsMixin, Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN ('backlog', 'todo', 'in_progress', 'in_review', 'done', 'cancelled')",
            name="tasks_status_in_enum",
        ),
        CheckConstraint(
            "priority IN ('none', 'low', 'medium', 'high', 'urgent')",
            name="tasks_priority_in_enum",
        ),
        # Hot-path indexes (TDD §17.1).
        Index("ix_tasks_project_id_status_created_at", "project_id", "status", "created_at"),
        Index("ix_tasks_assignee_id_due_date", "assignee_id", "due_date"),
        Index("ix_tasks_search_vector", "search_vector", postgresql_using="gin"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="backlog")
    priority: Mapped[str] = mapped_column(Text, nullable=False, default="none")
    assignee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # No ondelete on created_by (history-bearing FK; ADR 065 — users are anonymized in-place).
    created_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    # Generated column: tsvector(title weight A, description weight B). ADR 062.
    search_vector: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector('english', coalesce(title, '')), 'A') || "
            "setweight(to_tsvector('english', coalesce(description, '')), 'B')",
            persisted=True,
        ),
        nullable=False,
    )
