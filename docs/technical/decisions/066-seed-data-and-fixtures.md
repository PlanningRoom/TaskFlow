# Decision 066: Seed Data & Fixtures

**Status:** Decided

**Category:** Data Layer

**Question:** How is local/test/demo data populated?

**Options considered:**
- Idempotent Python seed script
- Factory library driven from tests
- Static SQL dump
- No seed

**Decision:** Idempotent Python seed script at `apps/api/taskflow/scripts/seed.py`.

Run via `make seed` (which executes `docker compose exec api python -m taskflow.scripts.seed`).

Seed output:
- One demo workspace ("Aurora Studio").
- Five users covering every role: 1 Owner, 1 Admin, 2 Members, 1 Viewer. Known email/password combos documented in the README.
- Three projects with varied access assignments.
- ~30 tasks covering every status (Backlog, To Do, In Progress, In Review, Done, plus a few Cancelled) and every priority level.
- All eight label colors exercised, with a few tasks carrying the max "+N" overflow indicator (PRD §7.2, DRD §7.5).
- Sample comments with @mentions to verify notification generation.
- A mix of read and unread notifications on the Member accounts.
- A range of due dates — overdue, approaching, future, none — to exercise the due-date visual treatments.

Script is idempotent: safe to re-run, wipes existing seed data by `workspace_id` before reinserting.

**Rationale:** A realistic seed is the single most useful dev-productivity tool. Essential for design QA against the DRD mockup, for E2E test baselines (Decision 080), and for demo presentations. Idempotency means it is safe to use routinely.
