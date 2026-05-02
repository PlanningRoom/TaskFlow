"""SQLAlchemy ORM models for TaskFlow (TDD §8.2)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from taskflow.db.uuid7 import uuid7

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map: dict[Any, Any] = {UUID: PGUUID(as_uuid=True)}


class UUIDPKMixin:
    """UUIDv7 primary key (TDD §8.2)."""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)


class CreatedAtMixin:
    """Append-only `created_at`."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class TimestampsMixin(CreatedAtMixin):
    """Mutable rows with `created_at` + `updated_at`."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
    )


# Re-exports — concrete models register themselves on Base.metadata at import time.
from taskflow.db.models.activity_event import ActivityEvent  # noqa: E402
from taskflow.db.models.audit_log import AuditLog  # noqa: E402
from taskflow.db.models.comment import Comment  # noqa: E402
from taskflow.db.models.invitation import Invitation  # noqa: E402
from taskflow.db.models.label import Label, TaskLabel  # noqa: E402
from taskflow.db.models.notification import Notification  # noqa: E402
from taskflow.db.models.password_reset_token import PasswordResetToken  # noqa: E402
from taskflow.db.models.project import Project, ProjectMembership  # noqa: E402
from taskflow.db.models.session import Session  # noqa: E402
from taskflow.db.models.task import Task  # noqa: E402
from taskflow.db.models.user import User  # noqa: E402
from taskflow.db.models.workspace import Workspace  # noqa: E402

__all__ = [
    "ActivityEvent",
    "AuditLog",
    "Base",
    "Comment",
    "CreatedAtMixin",
    "Invitation",
    "Label",
    "Notification",
    "PasswordResetToken",
    "Project",
    "ProjectMembership",
    "Session",
    "Task",
    "TaskLabel",
    "TimestampsMixin",
    "UUIDPKMixin",
    "User",
    "Workspace",
]
