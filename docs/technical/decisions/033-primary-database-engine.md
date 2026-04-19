# Decision 033: Primary Database Engine

**Status:** Decided

**Category:** Stack Foundations

**Question:** What is the primary datastore for TaskFlow?

**Options considered:**
- PostgreSQL
- MySQL / MariaDB
- SQLite

**Decision:** PostgreSQL 16+, running as a Docker container on the same EC2 host as the application (see Decision 036).

**Rationale:** Postgres gives us everything TaskFlow needs in one service: relational data, JSONB for activity/notification metadata, full-text search (Decision 062), `LISTEN/NOTIFY` for real-time pub-sub (Decision 045), and excellent Python support via asyncpg/SQLAlchemy. Running it as a container on the same EC2 avoids the cost of managed RDS — acceptable for a demonstration project. Backups handled by `pg_dump` to S3 (Decision 074).
