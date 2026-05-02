from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from taskflow.db.models import Base, CreatedAtMixin, UUIDPKMixin

# DRD §2.9 label palette (slugs). Migration `0001_initial.py` keeps the same list.
LABEL_COLORS = ("blue", "green", "red", "purple", "amber", "pink", "cyan", "orange")
_LABEL_COLOR_CHECK = "color IN (" + ", ".join(f"'{c}'" for c in LABEL_COLORS) + ")"


class Label(UUIDPKMixin, CreatedAtMixin, Base):
    __tablename__ = "labels"
    __table_args__ = (CheckConstraint(_LABEL_COLOR_CHECK, name="labels_color_in_palette"),)

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str] = mapped_column(Text, nullable=False)


class TaskLabel(Base):
    """Join table for tasks ↔ labels."""

    __tablename__ = "task_labels"

    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    label_id: Mapped[UUID] = mapped_column(
        ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True
    )
