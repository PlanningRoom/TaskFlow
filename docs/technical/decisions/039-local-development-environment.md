# Decision 039: Local Development Environment

**Status:** Decided

**Category:** Stack Foundations

**Question:** How does a developer run the full stack locally?

**Options considered:**
- Docker Compose (all services containerized)
- Native install (Postgres brew + `uvicorn --reload` + `vite dev`)
- devcontainers / Codespaces

**Decision:** Docker Compose. One command — `docker compose up` — starts:
- `api` — FastAPI with `--reload`, bind-mounted source (fast iteration)
- `web` — Vite dev server with HMR, bind-mounted source
- `db` — PostgreSQL 16 with a persistent named volume
- `mailhog` — SMTP sink for local email testing (invitations, password resets)

A `Makefile` provides ergonomic wrappers (`make dev`, `make test`, `make migrate`, `make seed`).

**Rationale:** User constraint — Docker for local dev. Compose matches production topology closely (same images, same Postgres version), reducing "works on my machine" bugs. MailHog stands in for Amazon SES locally. One-command start is the target for contributor onboarding.
