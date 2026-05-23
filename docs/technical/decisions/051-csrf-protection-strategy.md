# Decision 051: CSRF Protection Strategy

**Status:** Decided

**Category:** Auth Implementation

**Question:** How do we protect against cross-site request forgery?

**Options considered:**
- `SameSite=Lax` cookies only
- `SameSite` + double-submit CSRF token
- Synchronizer token pattern (server-issued per-session token)

**Decision:** Defense in depth:

1. Session cookie is `SameSite=Lax`, `HttpOnly`, `Secure` (Decision 047).
2. Server issues a `csrf_token` cookie (readable by JavaScript, not `HttpOnly`) on login — 32 random bytes, bound to the session.
3. Frontend reads the `csrf_token` cookie and echoes its value in an `X-CSRF-Token` header on every POST, PUT, PATCH, and DELETE request.
4. Server middleware validates that header value equals the cookie value and matches the active session's CSRF binding. Mismatch → 403.
5. Safe methods (GET, HEAD, OPTIONS) skip the check.

WebSocket upgrades rely on the session cookie + a CSRF token in the initial upgrade query parameter (`?csrf=…`). The server treats the upgrade as a state-changing request and runs the same `csrf_check(method="POST", header_token, cookie_token, session)` helper as the REST endpoints.

WebSocket close codes (RFC 6455 application-defined range 4000–4999):
- `4401` — unauthenticated (no/invalid session)
- `4403` — CSRF check failed
- `4500` — unexpected server error during setup

**Rationale:** `SameSite=Lax` alone blocks most CSRF, but a double-submit token costs almost nothing and defends against same-site sub-domain takeovers and top-level navigation edge cases. The cookie-echo pattern avoids server-side storage of per-request tokens.
