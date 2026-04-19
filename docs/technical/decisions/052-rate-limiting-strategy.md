# Decision 052: Rate Limiting Strategy

**Status:** Decided

**Category:** Auth Implementation

**Question:** Which endpoints are rate-limited, and with what backing store?

**Options considered:**
- None
- Per-IP / per-account limits via `slowapi`
- Global limiter at the edge (Cloudflare, AWS WAF)

**Decision:** `slowapi` (FastAPI rate-limit integration) with in-memory counters (single-instance deploy per Decision 036). Limits:

| Endpoint | Limit |
|---|---|
| `POST /api/v1/auth/login` | 5/min per IP, 10/min per email |
| `POST /api/v1/auth/password-reset` | 3/hour per IP, 3/hour per email |
| `POST /api/v1/auth/signup` | 3/hour per IP |
| `POST /api/v1/workspaces/invitations` | 20/hour per workspace |
| All other authenticated endpoints | 120/min per user |

429 responses follow the Decision 043 error contract with code `RATE_LIMITED` and a `Retry-After` header.

**Rationale:** Login brute-force, signup abuse, and invite spam are the realistic threats for a demo app. In-memory counters are fine for a single instance; switching to Redis is trivial if the deploy topology changes.
