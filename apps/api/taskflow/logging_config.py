"""structlog setup + request-context ASGI middleware (ADR 075, TDD §13.1).

All stdout is JSON. uvicorn's and FastAPI's stdlib loggers are bridged through
structlog's `ProcessorFormatter` so CloudWatch metric filters see one shape.

Pure ASGI middleware (rather than `BaseHTTPMiddleware`) is used because the
latter swallows / re-raises exceptions in ways that interact poorly with
FastAPI exception handlers — see starlette#1715.
"""

from __future__ import annotations

import logging
import sys
import time
import uuid
from typing import Any

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# stdlib loggers we explicitly bridge (their handlers are replaced).
_BRIDGED_STDLIB_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi")


def configure_logging(level: str = "info") -> None:
    """Configure structlog + bridge stdlib logs through structlog's ProcessorFormatter."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts")

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            # ProcessorFormatter expects this last — it strips/passes records through.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # Run shared processors on stdlib records so uvicorn lines also have ts/level.
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(log_level)

    # uvicorn installs its own handlers; replace them so we get one JSON shape.
    for name in _BRIDGED_STDLIB_LOGGERS:
        bridged = logging.getLogger(name)
        bridged.handlers = []
        bridged.propagate = True
        bridged.setLevel(log_level)


class RequestContextMiddleware:
    """Bind request-scoped fields into structlog contextvars and emit a log line per request."""

    def __init__(self, app: ASGIApp, *, header_name: str = "X-Request-Id") -> None:
        self.app = app
        self.header_name = header_name
        self._header_bytes = header_name.encode("latin-1")
        self._logger = structlog.get_logger("taskflow.request")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = self._read_header(scope.get("headers", []))
        request_id = incoming or uuid.uuid4().hex

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=scope.get("path", ""),
            method=scope.get("method", ""),
        )

        start = time.perf_counter()
        status_holder: dict[str, int] = {"status": 0}

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_holder["status"] = int(message.get("status", 0))
                headers = list(message.get("headers", []))
                headers = [(k, v) for (k, v) in headers if k.lower() != self._header_bytes.lower()]
                headers.append((self._header_bytes, request_id.encode("latin-1")))
                message = {**message, "headers": headers}
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            # logger.exception captures the active sys.exc_info() — single ERROR log
            # for any unhandled exception, with full request context bound.
            self._logger.exception("request.error", duration_ms=duration_ms, status=500)
            structlog.contextvars.clear_contextvars()
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        status = status_holder["status"]
        log = self._logger.error if status >= 500 else self._logger.info
        log("request", duration_ms=duration_ms, status=status)
        structlog.contextvars.clear_contextvars()

    def _read_header(self, headers: list[tuple[bytes, bytes]]) -> str | None:
        target = self._header_bytes.lower()
        for key, value in headers:
            if key.lower() == target:
                return value.decode("latin-1")
        return None
