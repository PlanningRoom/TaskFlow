"""FastAPI entry point (TDD §7.1)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import JSONResponse

from taskflow import __version__
from taskflow.api.v1 import api_router
from taskflow.api.v1.ws import websocket_endpoint
from taskflow.db.session import dispose_engine, get_engine, init_engine
from taskflow.errors import register_exception_handlers
from taskflow.logging_config import RequestContextMiddleware, configure_logging
from taskflow.rate_limit import limiter, rate_limit_exceeded_handler
from taskflow.realtime.after_commit import AfterCommitPublishMiddleware
from taskflow.realtime.bus import dispose_broadcaster, init_broadcaster
from taskflow.settings import settings

logger = structlog.get_logger()


class HealthStatus(BaseModel):
    """Response for `GET /health` (TDD §13.4)."""

    status: str


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging(settings.log_level)
    init_engine()
    await init_broadcaster()
    logger.info("app.startup", env=settings.app_env, version=__version__)
    try:
        yield
    finally:
        await dispose_broadcaster()
        await dispose_engine()
        logger.info("app.shutdown")


app = FastAPI(
    title="TaskFlow API",
    version=__version__,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs" if not settings.is_production else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.state.limiter = limiter
# Middleware registers innermost-first; request flow is the reverse:
# CORS → RequestContext → SlowAPI → AfterCommitPublish → route.
app.add_middleware(AfterCommitPublishMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token", "X-Request-Id"],
    expose_headers=["X-Request-Id"],
)

register_exception_handlers(app)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.include_router(api_router, prefix="/api/v1")

# WebSocket lives at root /ws per TDD §10.1 (not under /api/v1).
app.add_api_websocket_route("/ws", websocket_endpoint, name="websocket")


@app.get("/health", response_model=HealthStatus, tags=["health"])
async def health() -> JSONResponse:
    """Return 200 if Postgres is reachable, otherwise 503 (TDD §13.4)."""
    try:
        async with get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("health.db_unreachable")
        return JSONResponse({"status": "unhealthy"}, status_code=503)
    return JSONResponse({"status": "ok"})
