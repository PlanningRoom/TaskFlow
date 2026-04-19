# Decision 045: Real-Time Infrastructure

**Status:** Decided

**Category:** API & Real-Time

**Question:** What component fans out real-time events to connected clients?

**Options considered:**
- In-process FastAPI with Postgres LISTEN/NOTIFY
- In-process FastAPI with Redis pub/sub
- Managed realtime service (Pusher, Ably, Supabase Realtime)
- Postgres logical replication + change data capture

**Decision:** In-process FastAPI WebSocket handlers with PostgreSQL `LISTEN/NOTIFY` as the pub-sub bus, via the `broadcaster` Python library (channel backend: `postgres`). When a mutation commits, the transaction publishes a `NOTIFY` on a channel named per workspace/project; connected WebSocket handlers on any Uvicorn worker receive the notification and push to their subscribed clients.

**Rationale:** Keeps the stack to one EC2 host (Decision 036) with zero new services — no Redis, no managed third-party. Postgres is already present; `LISTEN/NOTIFY` is battle-tested for this use case and scales horizontally if we ever move to multiple app workers. If we later outgrow Postgres pub/sub (typically at thousands of concurrent connections), switching `broadcaster`'s backend to Redis is a configuration change.
