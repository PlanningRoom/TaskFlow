"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Body, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from taskflow.adapters.email import EmailMessage, set_email_sender
from taskflow.errors import ConflictError, NotFoundError, PermissionDeniedError
from taskflow.rate_limit import limiter


class FakeEmailSender:
    """In-memory recorder used in place of the SMTP/SES adapters in tests."""

    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []
        self.raise_on_send: Exception | None = None

    async def send(self, msg: EmailMessage) -> None:
        if self.raise_on_send is not None:
            raise self.raise_on_send
        self.sent.append(msg)


@pytest.fixture
def email_sender() -> Iterator[FakeEmailSender]:
    """Inject a `FakeEmailSender` for the duration of the test."""
    fake = FakeEmailSender()
    set_email_sender(fake)
    try:
        yield fake
    finally:
        set_email_sender(None)


@pytest.fixture(autouse=True)
def _default_fake_email_sender(request: pytest.FixtureRequest) -> Iterator[None]:
    """Replace the real email sender with a fake by default so tests that hit
    invitation/password-reset endpoints don't try to reach a live SMTP server.

    Tests that need to inspect sent mail should request the `email_sender`
    fixture explicitly; this autouse fixture only installs a throwaway fake.
    """
    if "email_sender" in request.fixturenames:
        yield
        return
    set_email_sender(FakeEmailSender())
    try:
        yield
    finally:
        set_email_sender(None)


@pytest.fixture(autouse=True)
def _disable_rate_limiter() -> Iterator[None]:
    """Disable slowapi for every test by default.

    Tests that exercise rate-limit behavior override this with a fixture that
    re-enables the limiter and resets its storage.
    """
    limiter.enabled = False
    try:
        yield
    finally:
        limiter.enabled = False
        limiter.reset()


class _EchoPayload(BaseModel):
    title: str


def _make_fake_engine(*, raises: Exception | None = None) -> MagicMock:
    fake_conn = AsyncMock()
    fake_conn.execute = AsyncMock(return_value=None)

    fake_engine_ctx = MagicMock()
    if raises is not None:
        fake_engine_ctx.__aenter__ = AsyncMock(side_effect=raises)
    else:
        fake_engine_ctx.__aenter__ = AsyncMock(return_value=fake_conn)
    fake_engine_ctx.__aexit__ = AsyncMock(return_value=None)

    fake_engine = MagicMock()
    fake_engine.connect = MagicMock(return_value=fake_engine_ctx)
    fake_engine.dispose = AsyncMock()
    return fake_engine


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A TestClient with the database mocked out so tests don't need Postgres."""
    fake_engine = _make_fake_engine()

    # init_engine and get_engine are imported into main's namespace; patch both
    # to keep the lifespan's init_engine() and the health route's get_engine() consistent.
    with (
        patch("taskflow.main.init_engine", return_value=fake_engine),
        patch("taskflow.main.get_engine", return_value=fake_engine),
        patch("taskflow.main.dispose_engine", new=AsyncMock()),
        patch("taskflow.main.init_broadcaster", new=AsyncMock(return_value=None)),
        patch("taskflow.main.dispose_broadcaster", new=AsyncMock()),
        patch("taskflow.main.init_scheduler", new=MagicMock(return_value=None)),
        patch("taskflow.main.shutdown_scheduler", new=MagicMock()),
    ):
        from taskflow.main import app

        # raise_server_exceptions=False mirrors real-client behavior: Starlette's
        # ServerErrorMiddleware always re-raises after sending the 500 response,
        # but a real HTTP client just sees the response. We test the wire shape.
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client


@pytest.fixture
def unhealthy_client() -> Iterator[TestClient]:
    """A TestClient where the database raises, exercising the 503 branch."""
    from sqlalchemy.exc import SQLAlchemyError

    fake_engine = _make_fake_engine(raises=SQLAlchemyError("connection refused"))

    with (
        patch("taskflow.main.init_engine", return_value=fake_engine),
        patch("taskflow.main.get_engine", return_value=fake_engine),
        patch("taskflow.main.dispose_engine", new=AsyncMock()),
        patch("taskflow.main.init_broadcaster", new=AsyncMock(return_value=None)),
        patch("taskflow.main.dispose_broadcaster", new=AsyncMock()),
        patch("taskflow.main.init_scheduler", new=MagicMock(return_value=None)),
        patch("taskflow.main.shutdown_scheduler", new=MagicMock()),
    ):
        from taskflow.main import app

        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client


@pytest.fixture
def app_with_test_routes(client: TestClient) -> Iterator[FastAPI]:
    """Mount throwaway routes on the live app so we can exercise error handlers."""
    from taskflow.main import app

    @app.post("/_test/echo")
    def _echo(payload: Annotated[_EchoPayload, Body()]) -> dict[str, str]:
        return {"title": payload.title}

    @app.get("/_test/not-found")
    def _not_found() -> None:
        raise NotFoundError("No such thing.", code="THING_NOT_FOUND")

    @app.get("/_test/forbidden")
    def _forbidden() -> None:
        raise PermissionDeniedError("Nope.", code="NOT_ALLOWED")

    @app.get("/_test/conflict")
    def _conflict() -> None:
        raise ConflictError("Already exists.", code="DUP")

    @app.get("/_test/explode")
    def _explode() -> None:
        raise RuntimeError("kaboom")

    yield app

    # Strip throwaway routes so other tests don't see them.
    app.router.routes = [
        r for r in app.router.routes if not getattr(r, "path", "").startswith("/_test/")
    ]
