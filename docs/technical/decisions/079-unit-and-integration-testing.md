# Decision 079: Unit & Integration Testing

**Status:** Decided

**Category:** Quality & Workflow

**Question:** Which framework runs unit and integration tests?

**Options considered:**
- Vitest (frontend) + pytest (backend)
- Jest (frontend) + pytest (backend)
- Node's built-in test runner (frontend) + pytest (backend)

**Decision:**
- **Frontend:** Vitest + React Testing Library + `@testing-library/user-event`. Vitest aligns with Vite (Decision 031), shares the build toolchain, and is drop-in Jest-compatible for API.
- **Backend:** pytest + `pytest-asyncio` for async tests + `httpx.AsyncClient` for FastAPI endpoint integration tests.

**Integration tests hit a real Postgres** — via the `db` service in a `docker-compose.test.yml` stack that CI spins up. No mocked database. Each test runs inside a transaction that is rolled back at the end, via a pytest fixture.

**Coverage target:** ≥70% on business-logic modules (auth, permissions, notifications, activity). Not enforced by a hard CI gate — serves as a directional signal.

**Rationale:** Vitest/pytest are the modern defaults for their respective ecosystems. Hitting a real Postgres is a non-negotiable pattern for TaskFlow — the workspace-scoped permission filters, full-text-search queries, and `LISTEN/NOTIFY` behavior are exactly the kind of code where mocked databases pass while production breaks.
