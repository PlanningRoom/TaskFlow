from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column

from taskflow.db.models import Base, TimestampsMixin, UUIDPKMixin

USER_ROLES = ("owner", "admin", "member", "viewer")


class User(UUIDPKMixin, TimestampsMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'admin', 'member', 'viewer')",
            name="users_role_in_enum",
        ),
        # Partial unique index: citext makes the comparison case-insensitive natively;
        # WHERE deleted_at IS NULL keeps the column reusable after anonymization.
        Index(
            "uq_users_workspace_id_email_active",
            "workspace_id",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str | None] = mapped_column(CITEXT(), nullable=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
