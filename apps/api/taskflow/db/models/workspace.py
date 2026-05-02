from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from taskflow.db.models import Base, CreatedAtMixin, UUIDPKMixin


class Workspace(UUIDPKMixin, CreatedAtMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    # No ondelete on created_by (history-bearing FK; ADR 065). use_alter=True breaks
    # the chicken-and-egg between workspaces ↔ users at table creation time.
    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", use_alter=True, name="fk_workspaces_created_by_users"),
        nullable=True,
    )
