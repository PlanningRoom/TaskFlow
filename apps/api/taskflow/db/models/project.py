from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from taskflow.db.models import Base, CreatedAtMixin, TimestampsMixin, UUIDPKMixin


class Project(UUIDPKMixin, TimestampsMixin, Base):
    __tablename__ = "projects"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(Text, nullable=True)
    # No ondelete on created_by (history-bearing FK; ADR 065).
    created_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class ProjectMembership(CreatedAtMixin, Base):
    """Project-level access (PRD §5.2)."""

    __tablename__ = "project_memberships"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
