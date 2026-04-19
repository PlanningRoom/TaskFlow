# Decision 047: Session Strategy

**Status:** Decided

**Category:** Auth Implementation

**Question:** How is an authenticated session represented between requests?

**Options considered:**
- Server-side sessions (opaque cookie + DB record)
- Stateless JWT
- Hybrid (JWT access + refresh token)

**Decision:** Server-side sessions.

- Session id: 32 random bytes, URL-safe base64-encoded, carried in an HttpOnly, Secure, `SameSite=Lax` cookie named `taskflow_session`.
- Server side: a `sessions` table keyed by the session id (stored hashed), with `user_id`, `created_at`, `last_seen_at`, `expires_at`, `ip`, `user_agent`.
- Absolute lifetime: 30 days. Idle timeout: 7 days (updated on each request).
- Logout, password change, user removal, and account deletion all delete matching session rows — revocation is instant.

**Rationale:** PRD §4.2 requires that removed users lose access immediately. JWT-based auth makes instant revocation painful (a deny-list that reimplements server-side sessions). Postgres is the natural session store (Decision 068) — no Redis required.
