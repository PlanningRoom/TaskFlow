# Decision 035: Database Migration Tooling

**Status:** Decided

**Category:** Stack Foundations

**Question:** How are schema changes versioned, reviewed, and applied?

**Options considered:**
- Alembic (SQLAlchemy-native)
- yoyo-migrations
- sqlx-style raw SQL + custom runner
- Atlas

**Decision:** Alembic.

**Rationale:** De facto standard for SQLAlchemy projects. Autogenerate detects ORM model changes but every migration is reviewed and hand-edited before merge. Forward-only in production (no `downgrade` executed against real data). Runs automatically on container startup via an entrypoint script; the deploy workflow (Decision 071) can opt to run migrations as a separate step before rolling the app container.
