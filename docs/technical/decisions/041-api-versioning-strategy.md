# Decision 041: API Versioning Strategy

**Status:** Decided

**Category:** API & Real-Time

**Question:** How are breaking changes to the API handled?

**Options considered:**
- URL-prefix versioning (`/api/v1/`)
- Header-based versioning
- No versioning
- Rolling additive changes only

**Decision:** URL prefix versioning. All endpoints under `/api/v1/`. FastAPI uses an `APIRouter(prefix="/api/v1")`.

**Rationale:** Minimal cost now, critical posture for a future-public API (Decision 013). Easy for callers to reason about. Breaking changes go into `/api/v2/` when needed — but for a demo project the expectation is that v1 is stable.
