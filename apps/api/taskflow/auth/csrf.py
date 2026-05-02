"""CSRF double-submit verification (ADR 051, TDD §11.3).

The cookie + `X-CSRF-Token` header carry the URL-safe base64 of 32 random bytes.
The session row stores the raw bytes (TDD §8.2 / §11.3). Comparison is bytewise
and constant-time via `hmac.compare_digest`.
"""

from __future__ import annotations

import hmac

from taskflow.auth.sessions import decode_csrf
from taskflow.db.models.session import Session as SessionModel

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def csrf_check(
    method: str,
    *,
    header_token: str | None,
    cookie_token: str | None,
    session: SessionModel | None,
) -> bool:
    """Return True if the request is exempt or its CSRF token is valid.

    Rules:
      - GET/HEAD/OPTIONS skip the check.
      - Mutating methods require: cookie present, header present, both equal,
        AND match the session's bound CSRF value.
    """
    if method.upper() in SAFE_METHODS:
        return True
    if not header_token or not cookie_token:
        return False
    if not hmac.compare_digest(header_token, cookie_token):
        return False
    if session is None:
        return False
    decoded = decode_csrf(header_token)
    if decoded is None:
        return False
    return hmac.compare_digest(decoded, bytes(session.csrf_token))
