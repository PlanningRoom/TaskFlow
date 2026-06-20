"""Rate limiting wiring (ADR 052, Phase E1).

Wraps slowapi with TaskFlow conventions:

- IP keys honor `X-Forwarded-For` (we sit behind nginx in prod).
- Composite limits (per-IP + per-email, per-IP + per-workspace) are expressed
  by stacking decorators with different `key_func`s.
- `RateLimitExceeded` is translated into the existing `RateLimitedError` so the
  ADR 043 error envelope and `Retry-After` header flow through the global
  handler in `errors.py`.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from taskflow.errors import RateLimitedError, app_error_handler
from taskflow.settings import settings


def _client_ip(request: Request) -> str:
    """Best-effort client IP: leftmost `X-Forwarded-For` entry, else socket peer."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    if request.client is not None:
        return request.client.host
    return "unknown"


def ip_key(request: Request) -> str:
    return _client_ip(request)


def _read_body_field(request: Request, field: str) -> str | None:
    """Peek at a JSON body field synchronously.

    Safe because slowapi runs the limiter check *after* FastAPI has already
    parsed the Pydantic body param — Starlette's `request._body` cache is
    populated at that point. slowapi 0.1.9 calls key_funcs synchronously, so
    we cannot `await request.body()` here.
    """
    cached: bytes | None = getattr(request, "_body", None)
    if not cached:
        return None
    try:
        data: Any = json.loads(cached)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    if isinstance(data, dict):
        value = data.get(field)
        if isinstance(value, str):
            return value.strip().lower()
    return None


def email_key_factory(field: str = "email") -> Any:
    """Build a sync key_func that returns `email:<lower>` from the JSON body.

    Falls back to the client IP when the body has no usable email, so the limit
    still applies in pathological cases instead of becoming a global single
    bucket.
    """

    def _key(request: Request) -> str:
        email = _read_body_field(request, field)
        if email:
            return f"email:{email}"
        return f"ip:{_client_ip(request)}"

    return _key


def workspace_key(request: Request) -> str:
    """Workspace-scoped key for authenticated endpoints.

    Uses the session cookie value as a stable per-session identifier. In
    TaskFlow each user belongs to exactly one workspace and typically has one
    active session, so per-session is a practical lower bound on per-workspace.
    If `request.state.workspace_id` has been populated by the auth dependency
    chain (preferred), use it directly.
    """
    workspace_id = getattr(request.state, "workspace_id", None)
    if workspace_id is not None:
        return f"workspace:{workspace_id}"
    cookie = request.cookies.get(settings.session_cookie_name)
    if cookie:
        return f"session:{cookie}"
    return f"ip:{_client_ip(request)}"


limiter = Limiter(key_func=ip_key, default_limits=[], enabled=settings.rate_limit_enabled)


def _retry_after_seconds(exc: RateLimitExceeded) -> int | None:
    """Best-effort retry-after derived from the limit's period."""
    limit = getattr(exc, "limit", None)
    if limit is None:
        return None
    inner = getattr(limit, "limit", limit)
    expiry = getattr(inner, "get_expiry", None)
    if callable(expiry):
        try:
            return int(expiry())
        except (TypeError, ValueError):
            return None
    return None


async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> JSONResponse:
    """Translate slowapi's RateLimitExceeded into our ADR 043 envelope."""
    assert isinstance(exc, RateLimitExceeded)
    translated = RateLimitedError(
        "Too many requests. Please try again later.",
        retry_after=_retry_after_seconds(exc),
    )
    return await app_error_handler(request, translated)
