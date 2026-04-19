# Decision 062: Full-Text Search Implementation

**Status:** Decided

**Category:** Data Layer

**Question:** How is global task search implemented?

**Options considered:**
- PostgreSQL full-text search (`tsvector` + GIN)
- `pg_trgm` trigram search
- Meilisearch / Typesense
- ILIKE with indexes

**Decision:** PostgreSQL full-text search.

- `tasks` table has a generated column `search_vector tsvector GENERATED ALWAYS AS (setweight(to_tsvector('english', coalesce(title, '')), 'A') || setweight(to_tsvector('english', coalesce(description, '')), 'B')) STORED`.
- GIN index on `search_vector`.
- Query endpoint uses `websearch_to_tsquery('english', :q)` so the user can type `foo -bar "exact phrase"` naturally.
- Results ranked by `ts_rank_cd` and filtered to projects the requesting user can access.
- Result limit 50; dropdown shows the first 8 per PRD §12.1.

**Rationale:** Postgres FTS is more than enough for demo-scale data (thousands of tasks). Title weight is higher than description weight, matching user intent. No second service, no extra operational burden.
