# Decision 034: Database Access Layer

**Status:** Decided

**Category:** Stack Foundations

**Question:** How does application code read and write the database?

**Options considered:**
- SQLAlchemy 2.0 async (ORM + Core)
- SQLModel (SQLAlchemy + Pydantic wrapper)
- Tortoise ORM
- Raw asyncpg
- Piccolo

**Decision:** SQLAlchemy 2.0 with `asyncio` and `asyncpg` driver. ORM models for domain entities; Core (`select()`, `insert()`) for analytical queries (activity feed, dashboards). Pydantic models (separate from ORM models) serve as request/response DTOs.

**Rationale:** SQLAlchemy 2.0 is the mature default for Python + Postgres, with full async support. Keeping ORM models and API DTOs separate (rather than using SQLModel's unified objects) avoids leaking internal schema shapes into the API contract (Decision 013). Supports complex queries (activity feed joins, FTS) without escape hatches.
