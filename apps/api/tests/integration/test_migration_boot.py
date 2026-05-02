"""Phase B2 — verify `alembic upgrade head` produces the schema we expect (TDD §8.2)."""

from __future__ import annotations

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.asyncio


EXPECTED_TABLES = {
    "activity_events",
    "alembic_version",
    "audit_log",
    "comments",
    "invitations",
    "labels",
    "notifications",
    "password_reset_tokens",
    "project_memberships",
    "projects",
    "sessions",
    "task_labels",
    "tasks",
    "users",
    "workspaces",
}


async def test_migration_creates_expected_tables(db_engine: None) -> None:
    from taskflow.db import session as session_module

    assert session_module._engine is not None
    async with session_module._engine.connect() as conn:
        rows = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        present = {r[0] for r in rows}
    missing = EXPECTED_TABLES - present
    assert not missing, f"missing tables after migration: {missing}"


async def test_required_indexes_exist(db_engine: None) -> None:
    from taskflow.db import session as session_module

    assert session_module._engine is not None
    expected_indexes = {
        # Hot-path indexes from TDD §17.1.
        "ix_tasks_project_id_status_created_at",
        "ix_tasks_assignee_id_due_date",
        "ix_tasks_search_vector",
        "ix_notifications_recipient_id_created_at",
        "ix_notifications_recipient_id_unread",
        "ix_activity_events_workspace_id_created_at",
        "ix_activity_events_project_id_created_at",
        "ix_sessions_user_id",
        "ix_sessions_expires_at",
        # Partial unique index for live-user emails (TDD §8.2).
        "uq_users_workspace_id_email_active",
    }
    async with session_module._engine.connect() as conn:
        rows = await conn.execute(
            text("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
        )
        present = {r[0] for r in rows}
    missing = expected_indexes - present
    assert not missing, f"missing indexes: {missing}"


async def test_users_role_check_constraint_rejects_unknown_role(db_engine: None) -> None:
    from sqlalchemy.exc import IntegrityError

    from taskflow.db import session as session_module
    from taskflow.db.uuid7 import uuid7

    assert session_module._session_factory is not None

    async with session_module._session_factory() as s:
        # Workspace first.
        ws_id = uuid7()
        await s.execute(
            text("INSERT INTO workspaces (id, name) VALUES (:id, 'wks')"),
            {"id": str(ws_id)},
        )
        await s.commit()

        with pytest.raises(IntegrityError):
            await s.execute(
                text(
                    "INSERT INTO users (id, workspace_id, email, role) "
                    "VALUES (:id, :ws, 'a@b.c', 'bogus')"
                ),
                {"id": str(uuid7()), "ws": str(ws_id)},
            )
            await s.commit()


async def test_tasks_search_vector_is_generated(db_engine: None) -> None:
    """Inserting a task populates `search_vector` automatically (ADR 062)."""
    from taskflow.db import session as session_module
    from taskflow.db.uuid7 import uuid7

    assert session_module._session_factory is not None

    async with session_module._session_factory() as s:
        ws_id, project_id, task_id = uuid7(), uuid7(), uuid7()
        await s.execute(
            text("INSERT INTO workspaces (id, name) VALUES (:id, 'wks')"),
            {"id": str(ws_id)},
        )
        await s.execute(
            text("INSERT INTO projects (id, workspace_id, name) VALUES (:id, :ws, 'p1')"),
            {"id": str(project_id), "ws": str(ws_id)},
        )
        await s.execute(
            text(
                "INSERT INTO tasks (id, project_id, workspace_id, title, description, "
                "status, priority) VALUES (:id, :pid, :ws, 'Refactor login', "
                "'fix the password reset flow', 'backlog', 'none')"
            ),
            {"id": str(task_id), "pid": str(project_id), "ws": str(ws_id)},
        )
        await s.commit()

        result = await s.execute(
            text(
                "SELECT search_vector::text FROM tasks "
                "WHERE search_vector @@ websearch_to_tsquery('english', :q)"
            ),
            {"q": "password"},
        )
        rows = result.all()
    assert rows, "FTS query should match the inserted task on description content"
