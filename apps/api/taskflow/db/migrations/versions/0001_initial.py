"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-02

Creates all 14 tables (TDD §8.2) with hot-path indexes (TDD §17.1), CHECK
constraints for enum-like text columns, the partial unique index on
`users(workspace_id, email) WHERE deleted_at IS NULL`, the generated
`tasks.search_vector` tsvector + GIN index (ADR 062), and the canonical
audit-event CHECK constraint (ADR 084).

History-bearing FKs (`comments.author_id`, `tasks.created_by`,
`activity_events.actor_id`, `audit_log.actor_id`, `notifications.actor_id`)
have NO `ondelete` — users are anonymized in-place, never hard-deleted (ADR 065).
`tasks.assignee_id` keeps `ondelete="SET NULL"` per ADR 065's explicit rule.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Source of truth: ADR 084. Adding an event requires a migration that ALTERs the
# CHECK constraint below.
AUDIT_EVENT_TYPES = (
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
AUDIT_EVENT_CHECK = "event_type IN (" + ", ".join(f"'{e}'" for e in AUDIT_EVENT_TYPES) + ")"

# Source of truth: DRD §2.9 (label palette). Stored as slugs.
LABEL_COLORS = ("blue", "green", "red", "purple", "amber", "pink", "cyan", "orange")
LABEL_COLOR_CHECK = "color IN (" + ", ".join(f"'{c}'" for c in LABEL_COLORS) + ")"


def upgrade() -> None:
    # citext for case-insensitive email comparison (TDD §8.2).
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    # ───────── workspaces ─────────
    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workspaces"),
    )

    # ───────── users ─────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
            name="fk_users_workspace_id_workspaces",
        ),
        sa.CheckConstraint(
            "role IN ('owner', 'admin', 'member', 'viewer')",
            name="ck_users_users_role_in_enum",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index(
        "uq_users_workspace_id_email_active",
        "users",
        ["workspace_id", "email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # workspaces.created_by FK — no ondelete (history-bearing FKs remain intact, ADR 065).
    op.create_foreign_key(
        "fk_workspaces_created_by_users",
        "workspaces",
        "users",
        ["created_by"],
        ["id"],
        use_alter=True,
    )

    # ───────── sessions ─────────
    op.create_table(
        "sessions",
        sa.Column("id", sa.LargeBinary(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("csrf_token", sa.LargeBinary(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name="fk_sessions_user_id_users"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_sessions"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_sessions_expires_at", "sessions", ["expires_at"])

    # ───────── invitations ─────────
    op.create_table(
        "invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", postgresql.CITEXT(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.LargeBinary(), nullable=False),
        sa.Column("invited_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
            name="fk_invitations_workspace_id_workspaces",
        ),
        sa.ForeignKeyConstraint(
            ["invited_by"], ["users.id"], ondelete="CASCADE", name="fk_invitations_invited_by_users"
        ),
        sa.CheckConstraint(
            "role IN ('owner', 'admin', 'member', 'viewer')",
            name="ck_invitations_invitations_role_in_enum",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_invitations"),
        sa.UniqueConstraint("token_hash", name="uq_invitations_token_hash"),
    )

    # ───────── password_reset_tokens ─────────
    op.create_table(
        "password_reset_tokens",
        sa.Column("token_hash", sa.LargeBinary(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="fk_password_reset_tokens_user_id_users",
        ),
        sa.PrimaryKeyConstraint("token_hash", name="pk_password_reset_tokens"),
    )
    op.create_index(
        "ix_password_reset_tokens_user_id",
        "password_reset_tokens",
        ["user_id"],
    )

    # ───────── projects ─────────
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("color", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
            name="fk_projects_workspace_id_workspaces",
        ),
        # No ondelete on created_by (history-bearing FK; ADR 065).
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name="fk_projects_created_by_users",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
    )
    op.create_index("ix_projects_workspace_id", "projects", ["workspace_id"])

    # ───────── project_memberships ─────────
    op.create_table(
        "project_memberships",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
            name="fk_project_memberships_project_id_projects",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="fk_project_memberships_user_id_users",
        ),
        sa.PrimaryKeyConstraint("project_id", "user_id", name="pk_project_memberships"),
    )

    # ───────── tasks ─────────
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("priority", sa.Text(), nullable=False),
        sa.Column("assignee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR(),
            sa.Computed(
                "setweight(to_tsvector('english', coalesce(title, '')), 'A') || "
                "setweight(to_tsvector('english', coalesce(description, '')), 'B')",
                persisted=True,
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE", name="fk_tasks_project_id_projects"
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
            name="fk_tasks_workspace_id_workspaces",
        ),
        # tasks.assignee_id: SET NULL on user delete (PRD §4.2 / ADR 065 explicit rule).
        sa.ForeignKeyConstraint(
            ["assignee_id"],
            ["users.id"],
            ondelete="SET NULL",
            name="fk_tasks_assignee_id_users",
        ),
        # No ondelete on created_by (history-bearing FK; ADR 065).
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="fk_tasks_created_by_users"
        ),
        sa.CheckConstraint(
            "status IN ('backlog', 'todo', 'in_progress', 'in_review', 'done', 'cancelled')",
            name="ck_tasks_tasks_status_in_enum",
        ),
        sa.CheckConstraint(
            "priority IN ('none', 'low', 'medium', 'high', 'urgent')",
            name="ck_tasks_tasks_priority_in_enum",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tasks"),
    )
    op.create_index("ix_tasks_workspace_id", "tasks", ["workspace_id"])
    op.create_index(
        "ix_tasks_project_id_status_created_at",
        "tasks",
        ["project_id", "status", sa.text("created_at DESC")],
    )
    op.create_index("ix_tasks_assignee_id_due_date", "tasks", ["assignee_id", "due_date"])
    op.create_index(
        "ix_tasks_search_vector",
        "tasks",
        ["search_vector"],
        postgresql_using="gin",
    )

    # ───────── labels ─────────
    op.create_table(
        "labels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("color", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
            name="fk_labels_workspace_id_workspaces",
        ),
        sa.CheckConstraint(LABEL_COLOR_CHECK, name="ck_labels_color_in_palette"),
        sa.PrimaryKeyConstraint("id", name="pk_labels"),
    )
    op.create_index("ix_labels_workspace_id", "labels", ["workspace_id"])

    # ───────── task_labels ─────────
    op.create_table(
        "task_labels",
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_id"], ["tasks.id"], ondelete="CASCADE", name="fk_task_labels_task_id_tasks"
        ),
        sa.ForeignKeyConstraint(
            ["label_id"], ["labels.id"], ondelete="CASCADE", name="fk_task_labels_label_id_labels"
        ),
        sa.PrimaryKeyConstraint("task_id", "label_id", name="pk_task_labels"),
    )

    # ───────── comments ─────────
    op.create_table(
        "comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["task_id"], ["tasks.id"], ondelete="CASCADE", name="fk_comments_task_id_tasks"
        ),
        # No ondelete on author_id (history-bearing FK; ADR 065).
        sa.ForeignKeyConstraint(
            ["author_id"], ["users.id"], name="fk_comments_author_id_users"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_comments"),
    )
    op.create_index("ix_comments_task_id", "comments", ["task_id"])

    # ───────── activity_events ─────────
    op.create_table(
        "activity_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("subject_type", sa.Text(), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
            name="fk_activity_events_workspace_id_workspaces",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
            name="fk_activity_events_project_id_projects",
        ),
        # No ondelete on actor_id (history-bearing FK; ADR 065).
        sa.ForeignKeyConstraint(
            ["actor_id"], ["users.id"], name="fk_activity_events_actor_id_users"
        ),
        sa.CheckConstraint(
            "event_type IN ('task.created', 'task.status_changed', 'task.assigned', "
            "'task.unassigned', 'comment.created')",
            name="ck_activity_events_activity_events_event_type_in_enum",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_activity_events"),
    )
    op.create_index(
        "ix_activity_events_workspace_id_created_at",
        "activity_events",
        ["workspace_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "ix_activity_events_project_id_created_at",
        "activity_events",
        ["project_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "ix_activity_events_actor_id_created_at",
        "activity_events",
        ["actor_id", sa.text("created_at DESC")],
    )

    # ───────── notifications ─────────
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["recipient_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="fk_notifications_recipient_id_users",
        ),
        # No ondelete on actor_id (history-bearing FK; ADR 065).
        sa.ForeignKeyConstraint(
            ["actor_id"], ["users.id"], name="fk_notifications_actor_id_users"
        ),
        sa.ForeignKeyConstraint(
            ["task_id"], ["tasks.id"], ondelete="CASCADE", name="fk_notifications_task_id_tasks"
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
            name="fk_notifications_project_id_projects",
        ),
        sa.CheckConstraint(
            "event_type IN ('mention', 'task_assigned', 'task_status_changed', 'task_commented')",
            name="ck_notifications_notifications_event_type_in_enum",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_notifications"),
    )
    op.create_index(
        "ix_notifications_recipient_id_created_at",
        "notifications",
        ["recipient_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "ix_notifications_recipient_id_unread",
        "notifications",
        ["recipient_id"],
        postgresql_where=sa.text("read_at IS NULL"),
    )

    # ───────── audit_log ─────────
    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ip", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # No ondelete on actor_id (history-bearing FK; ADR 065).
        sa.ForeignKeyConstraint(
            ["actor_id"], ["users.id"], name="fk_audit_log_actor_id_users"
        ),
        sa.CheckConstraint(AUDIT_EVENT_CHECK, name="ck_audit_log_event_type_in_enum"),
        sa.PrimaryKeyConstraint("id", name="pk_audit_log"),
    )
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_log_created_at", table_name="audit_log")
    op.drop_table("audit_log")
    op.drop_index("ix_notifications_recipient_id_unread", table_name="notifications")
    op.drop_index("ix_notifications_recipient_id_created_at", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("ix_activity_events_actor_id_created_at", table_name="activity_events")
    op.drop_index("ix_activity_events_project_id_created_at", table_name="activity_events")
    op.drop_index("ix_activity_events_workspace_id_created_at", table_name="activity_events")
    op.drop_table("activity_events")
    op.drop_index("ix_comments_task_id", table_name="comments")
    op.drop_table("comments")
    op.drop_table("task_labels")
    op.drop_index("ix_labels_workspace_id", table_name="labels")
    op.drop_table("labels")
    op.drop_index("ix_tasks_search_vector", table_name="tasks")
    op.drop_index("ix_tasks_assignee_id_due_date", table_name="tasks")
    op.drop_index("ix_tasks_project_id_status_created_at", table_name="tasks")
    op.drop_index("ix_tasks_workspace_id", table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("project_memberships")
    op.drop_index("ix_projects_workspace_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_table("invitations")
    op.drop_index("ix_sessions_expires_at", table_name="sessions")
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_constraint("fk_workspaces_created_by_users", "workspaces", type_="foreignkey")
    op.drop_index("uq_users_workspace_id_email_active", table_name="users")
    op.drop_table("users")
    op.drop_table("workspaces")
    op.execute("DROP EXTENSION IF EXISTS citext")
