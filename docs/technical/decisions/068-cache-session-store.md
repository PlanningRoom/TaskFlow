# Decision 068: Cache / Session Store

**Status:** Decided

**Category:** Supporting Services

**Question:** Do we run a separate cache/session store (Redis), or use Postgres?

**Options considered:**
- Redis
- Postgres-only
- Managed KV
- In-process memory + Postgres

**Decision:** PostgreSQL only.

- Sessions in `sessions` table (Decision 047).
- Rate-limit counters in `slowapi`'s in-memory store (Decision 052) — acceptable because the production topology is a single Uvicorn instance (Decision 036).
- No application-level read cache at launch. If a specific query becomes hot, we add a targeted cache — in-memory first, Redis only if horizontal scaling requires it.

**Rationale:** A `t4g.small` has 2 GB RAM; adding Redis would halve what is available to Postgres and the app. For demo-scale load, Postgres handles session lookups in microseconds when the `sessions` table is properly indexed. Every avoided service is an avoided failure mode.
