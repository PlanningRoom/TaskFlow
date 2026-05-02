"""Postgres-backed integration test fixtures.

These fixtures connect to a real Postgres at `TEST_DATABASE_URL` (default
`postgresql+asyncpg://taskflow:taskflow@localhost:5432/taskflow_test`). The
schema is rebuilt by running Alembic to head once per session.

Tests that don't need the DB live in `tests/integration/` too; they can
ignore these fixtures. Tests that DO need the DB request `db_engine` /
`db_session`. If Postgres isn't reachable the fixtures call
`pytest.skip(...)` and dependent tests are skipped — this lets the existing
no-DB tests keep running locally without Docker.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DEFAULT_TEST_DB_URL = "postgresql+asyncpg://taskflow:taskflow@localhost:5432/taskflow_test"


def _test_database_url() -> str:
    return os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DB_URL)


async def _reset_schema(url: str) -> None:
    engine = create_async_engine(url, future=True, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
def _alembic_config() -> Config:
    project_root = Path(__file__).resolve().parents[2]
    cfg = Config(str(project_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(project_root / "taskflow" / "db" / "migrations"))
    cfg.set_main_option("sqlalchemy.url", _test_database_url())
    return cfg


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-mark every test that uses `db_engine` / `db_session` with `requires_db`.

    Tests that explicitly carry the marker also get the early-skip behavior.
    """
    db_fixtures = {"db_engine", "db_session"}
    for item in items:
        if isinstance(item, pytest.Function) and db_fixtures & set(item.fixturenames):
            item.add_marker(pytest.mark.requires_db)


@pytest.fixture(scope="session")
def _migrated_database(_alembic_config: Config) -> Iterator[str]:
    """Drop everything and run `alembic upgrade head` once per test session."""
    url = _test_database_url()
    try:
        asyncio.run(_reset_schema(url))
    except (OperationalError, OSError) as exc:
        pytest.skip(f"Postgres at {url!r} not reachable: {exc}")

    command.upgrade(_alembic_config, "head")
    yield url


_TRUNCATE_SQL = (
    "TRUNCATE workspaces, users, sessions, invitations, password_reset_tokens, "
    "projects, project_memberships, tasks, labels, task_labels, comments, "
    "activity_events, notifications, audit_log RESTART IDENTITY CASCADE"
)


@pytest.fixture
async def db_engine(_migrated_database: str) -> AsyncIterator[None]:
    """Per-test: point the app's engine at the test DB and truncate on teardown.

    Runs for every DB-backed test (auto-marked via `pytest_collection_modifyitems`),
    not just those that request `db_session` directly — so data never leaks between
    tests that exercise the API but don't query the DB themselves.
    """
    from taskflow.db import session as session_module

    await session_module.dispose_engine()
    real_engine = create_async_engine(_migrated_database, future=True, pool_pre_ping=True)
    real_factory = async_sessionmaker(real_engine, expire_on_commit=False, class_=AsyncSession)

    session_module._engine = real_engine
    session_module._session_factory = real_factory

    try:
        yield
    finally:
        async with real_engine.begin() as conn:
            await conn.execute(text(_TRUNCATE_SQL))
        await session_module.dispose_engine()


@pytest.fixture
async def db_session(db_engine: None) -> AsyncIterator[AsyncSession]:
    """Yield an `AsyncSession` against the migrated test DB.

    The session has `expire_on_commit=False`, so use `db_session.expire_all()`
    or `db_session.refresh(obj)` after a mutation that goes through the API
    (separate session) before re-reading the row.
    """
    from taskflow.db import session as session_module

    assert session_module._session_factory is not None
    async with session_module._session_factory() as session:
        yield session
        await session.rollback()
