# Decision 069: Background Job System

**Status:** Decided

**Category:** Supporting Services

**Question:** How are asynchronous tasks executed?

**Options considered:**
- Postgres-backed queue (`arq`, custom)
- Redis-backed queue (RQ, Celery, Dramatiq)
- Inline execution + scheduler
- Cloud queue (SQS)

**Decision:** Two light-weight mechanisms, no dedicated worker process:

1. **FastAPI `BackgroundTasks`** for in-request async fire-and-forget (e.g., "send invitation email after the HTTP response"). Runs on the same Uvicorn event loop. If the process restarts mid-task, the task is lost — acceptable for email; invitations can be re-sent (PRD §3.3).

2. **APScheduler `AsyncIOScheduler`** running in the FastAPI process for periodic jobs:
   - Expire invitations older than 7 days (every 15 minutes).
   - Delete expired sessions (daily).
   - Delete expired password-reset tokens (daily).
   - `pg_dump` to S3 backup (nightly — see Decision 074).

**Rationale:** The async surface is small and non-critical — no financial or regulatory work that must survive process restart. Avoiding a separate worker and avoiding Redis keeps the EC2 footprint minimal. If background work later grows in importance, `arq` on Redis is a drop-in upgrade path.
