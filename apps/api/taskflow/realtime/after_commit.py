"""Request-scoped after-commit publish queue.

TDD §10.2 requires publish to happen *after* the service transaction commits.
Endpoints call `schedule_publish(request, publisher)` to enqueue a zero-arg
async callable; the `AfterCommitPublishMiddleware` drains the queue after a
successful response (HTTP < 400). On error responses, the queue is dropped —
clients reconcile via refetch (TDD §10.4).

Implementation note: Starlette's `Request.state` proxies `scope["state"]`, so
endpoints and the middleware share the same dict via that key.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

if TYPE_CHECKING:
    from starlette.requests import Request

logger = structlog.get_logger()

type PublishCallable = Callable[[], Awaitable[None]]
type PendingPublish = PublishCallable

_QUEUE_KEY = "pending_publishes"


def pending_publishes(request: Request) -> list[PublishCallable]:
    """Return (lazily initialized) the request-scoped publish queue."""
    queue = getattr(request.state, _QUEUE_KEY, None)
    if queue is None:
        queue = []
        setattr(request.state, _QUEUE_KEY, queue)
    return queue


def schedule_publish(request: Request, publisher: PublishCallable) -> None:
    """Queue a publisher coroutine factory to run after the response is sent."""
    pending_publishes(request).append(publisher)


class AfterCommitPublishMiddleware:
    """ASGI middleware that drains the publish queue after a 2xx/3xx response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        status_holder: dict[str, int] = {"status": 500}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                status_holder["status"] = int(message.get("status", 500))
            await send(message)

        await self.app(scope, receive, send_wrapper)

        if status_holder["status"] >= 400:
            return
        state = scope.get("state") or {}
        queue: list[PublishCallable] = state.get(_QUEUE_KEY) or []
        for publisher in queue:
            try:
                await publisher()
            except Exception as exc:  # noqa: BLE001 — never propagate after the response
                logger.warning("realtime.after_commit_publish_failed", error=str(exc))
