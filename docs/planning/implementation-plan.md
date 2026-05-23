# TaskFlow — Implementation Plan

**Version:** 1.0
**Date:** 2026-04-25
**Status:** Draft
**Approach:** Backend-first / API-complete

---

## 1. Introduction

### 1.1 Purpose

This document is the build plan for TaskFlow. It sequences the work in a way that lets one developer (or a small team) construct the system described in the BRD, PRD, DRD, and TDD without rework. Every phase is traceable back to specific Architectural Decision Records (ADRs) and to numbered sections of the requirements documents.

### 1.2 Approach

The chosen sequence is **Backend-first / API-complete**: build the entire FastAPI backend — schema, migrations, auth, every `/api/v1` endpoint, real-time, background jobs, security, and tests — before any frontend code is written. Once the API is complete and integration-tested, build the React SPA against the live backend with generated TypeScript types as the contract. CloudFormation, CD, and the production cutover come last, after end-to-end tests pass against a local stack.

The motivations for this order:

- The OpenAPI schema becomes a stable contract. Codegen (ADR 042) produces frontend types that cannot drift from server reality.
- Workspace isolation, permission rules, and real-time fan-out (the project's hardest correctness questions) are settled before any UI assumption is baked in.
- Integration tests carry most of the verification load. A backend with thorough integration coverage protects every later UI change.
- The frontend track becomes mostly mechanical: render screens, wire queries, handle loading/error/empty states.

The trade-off accepted: no clickable UI exists until Part F. Design changes after Part F that affect data shape will require backend revision. To mitigate, the existing `docs/design/mockup.html` and the DRD remain the design contract — no major design re-evaluation is expected during the build.

### 1.3 Reference Documents

| Document | Location |
|----------|----------|
| Business Overview | [../business/business-overview.md](../business/business-overview.md) |
| Business Requirements Document | [../business/business-requirements-document.md](../business/business-requirements-document.md) |
| Product Requirements Document | [../product/product-requirements-document.md](../product/product-requirements-document.md) |
| Design Requirements Document | [../design/design-requirements-document.md](../design/design-requirements-document.md) |
| Technical Design Document | [../technical/technical-design-document.md](../technical/technical-design-document.md) |
| Business Decision Records | [../business/decisions/INDEX.md](../business/decisions/INDEX.md) |
| Product Decision Records | [../product/decisions/INDEX.md](../product/decisions/INDEX.md) |
| Design Decision Records | [../design/decisions/INDEX.md](../design/decisions/INDEX.md) |
| Architectural Decision Records | [../technical/decisions/INDEX.md](../technical/decisions/INDEX.md) |
| Implementation Status Tracker | [./implementation-status.md](./implementation-status.md) |

ADRs are cited inline as `(ADR NNN)` throughout this document.

---

## 2. Sequencing Principles

1. **Contracts before consumers.** The API contract (OpenAPI) and the data model are stable before any UI consumes them. Within the backend, services are stable before WebSockets are layered on top of them.
2. **One feature complete before the next starts.** A feature is "complete" only when its endpoints, services, persistence, real-time emission, audit log entry, integration tests, and seed data fixtures all land in the same phase.
3. **Cross-cutting first.** Auth, permissions, error contract, logging, and the broadcaster bus are built before the first feature so each feature plugs into them rather than retrofitting.
4. **Tests live with the code that produces them.** Each backend phase finishes with integration tests for its endpoints across roles and project access. Each frontend phase finishes with component tests for its screens.
5. **No production work until acceptance is green.** CloudFormation, OIDC, and DNS happen after Playwright passes locally end-to-end against a `docker compose up` stack.

---

## 3. Phase Map

| Part | Phases | Theme |
|------|--------|-------|
| **A** | Phase 0 | Project foundation |
| **B** | B1 → B4 | Backend core (skeleton, schema, auth core, auth endpoints) |
| **C** | C1 → C8 | Backend domain (workspace, labels, projects, tasks, comments, activity, notifications, search, dashboard) |
| **D** | D1 → D2 | Backend real-time and async (WebSocket, background jobs, email) |
| **E** | E1 → E4 | Backend hardening (security, observability, test completion, seed data) |
| **F** | F1 → F4 | Frontend foundation (skeleton, API client, primitives, app shell) |
| **G** | G1 → G8 | Frontend screens (auth, dashboard, board, list, task panel, notifications, search, settings) |
| **H** | H1 → H5 | Frontend cross-cutting (real-time, empty states, toasts, accessibility, tests) |
| **I** | I1 → I6 | E2E, infrastructure, deployment, monitoring, acceptance |

**Total: 42 phases.** Phase sizes target 1–3 days of focused work each. Parts B–E (backend) are the longest stretch.

---

## 4. Detailed Phases

Each phase below includes a goal, the concrete tasks, the deliverables, the definition of done, and the references that drove its scope.

---

### Part A — Foundation

#### Phase 0 — Project Foundation

**Goal:** Stand up the monorepo with build tooling, local dev stack, and basic CI before any application code is written.

**Tasks:**
- Initialize pnpm workspaces monorepo with Turborepo (ADR 026). Layout per TDD §4.
- Create `apps/web`, `apps/api`, `packages/api-types`, `packages/config`, `infra/`, `.github/workflows/` directories per TDD §4 tree.
- Add `pnpm-workspace.yaml`, `turbo.json`, root `package.json`, `Makefile`.
- Configure Biome (ADR 078): root `biome.json` extends `packages/config/biome.base.json` so other workspaces can share the base. Configure Ruff for `apps/api` via `[tool.ruff]` in `pyproject.toml` (ADR 078).
- Set up Python 3.12+ with `pyproject.toml` (ADR 028); manage deps with `uv` (lockfile committed at `apps/api/uv.lock`).
- Author `docker-compose.yml` (dev), `docker-compose.test.yml` (integration), `docker-compose.prod.yml` (placeholder) per TDD §15.1.
- Author `apps/web/Dockerfile` and `apps/api/Dockerfile` (stubs OK; both `linux/arm64`, ADR 038).
- Add MailHog service to `docker-compose.yml` (TDD §15.1).
- Author `.env.example` covering all runtime config keys.
- Set up GitHub Actions `ci.yml` with two initial jobs: `lint` (Biome + Ruff) and `typecheck` (placeholder until apps exist).
- Configure Dependabot and CodeQL on the repo (ADR 086).
- Configure pre-commit hooks (ADR 082): Husky + lint-staged for Biome on staged TS/JS; `pre-commit` framework for Ruff on Python and `detect-secrets` on staged content.
- Add root `README.md` (development quickstart).

**Deliverables:** A repo where `make dev` boots the dev stack with empty placeholder services, and `make lint` / `make typecheck` succeed on the empty apps.

**Definition of done:**
- `pnpm install` succeeds at the root.
- `docker compose up` starts the dev stack (db + mailhog + placeholder api/web) without errors.
- CI runs `lint` and `typecheck` jobs on PR with green output.
- Pre-commit hook blocks a commit containing a fake API key.

**References:** ADRs 026, 028, 038, 039, 071, 078, 082, 086 · TDD §4, §15

---

### Part B — Backend Core

#### Phase B1 — Backend Skeleton

**Goal:** A minimal FastAPI application that boots, serves `/health`, returns the standard error envelope, and emits structured logs.

**Tasks:**
- Add FastAPI + Uvicorn (ADR 032) to `apps/api`. Configure ASGI entry point in `taskflow/main.py`.
- Implement `taskflow/settings.py` using `pydantic-settings` (ADR 042). Read from env; for prod, env will be hydrated from SSM at boot (ADR 073).
- Implement `taskflow/db/session.py` — async SQLAlchemy engine + session dependency (ADR 034) using asyncpg.
- Configure Alembic (ADR 035) with `alembic.ini` and `db/migrations/env.py` reading the same DB URL as the app.
- Implement the global error contract (ADR 043) in `taskflow/errors.py`: handlers for `RequestValidationError`, application exceptions (`NotFoundError`, `PermissionDeniedError`, `ConflictError`, `RateLimitedError`), and unhandled `Exception` (logged, 500, opaque envelope).
- Configure structured logging (ADR 075) with `structlog`: JSON to stdout, request-id middleware, fields per TDD §13.1.
- Implement `GET /health` returning 200 if `SELECT 1` succeeds, 503 otherwise (TDD §13.4).
- Implement API versioning prefix `/api/v1` (ADR 041) and an empty router for v1.
- Wire OpenAPI generation; expose `/api/v1/openapi.json` (TDD §9.3).
- Add `mypy` to CI typecheck job.

**Deliverables:** A FastAPI app that boots inside `docker compose`, responds to `/health`, exposes an empty but valid OpenAPI schema, and produces structured JSON logs.

**Definition of done:**
- `curl localhost/health` returns 200.
- `curl localhost/api/v1/openapi.json` returns a valid OpenAPI 3.1 document.
- A handled error returns the ADR 043 envelope; an unhandled error returns 500 with the same envelope and emits an ERROR log line.
- `mypy` passes on `apps/api/taskflow`.

**References:** ADRs 032, 034, 035, 040, 041, 042, 043, 073, 075 · TDD §7.1, §9, §13.1, §13.4

---

#### Phase B2 — Database Schema and Migrations

**Goal:** Every table from the data model exists in Postgres via Alembic, with the indexes needed by the hot paths.

**Tasks:**
- Define SQLAlchemy 2.0 ORM models for every table in TDD §8.2: `workspaces`, `users`, `sessions`, `invitations`, `password_reset_tokens`, `projects`, `project_memberships`, `tasks`, `labels`, `task_labels`, `comments`, `activity_events`, `notifications`, `audit_log`.
- UUIDv7 primary keys (TDD §8.2). Add `created_at` / `updated_at` `timestamptz` columns where the model dictates.
- Add the partial unique index on `users(workspace_id, lower(email)) WHERE deleted_at IS NULL`.
- Add `tasks.search_vector` as a generated column from `title` + `description`; create the GIN index (ADR 062).
- Add hot-path indexes per TDD §17.1: `tasks(project_id, status, created_at DESC)`, `tasks(assignee_id, due_date)`, `notifications(recipient_id, created_at DESC)`, partial `notifications(recipient_id) WHERE read_at IS NULL`, `activity_events(workspace_id, created_at DESC)`, `activity_events(project_id, created_at DESC)`, `sessions(user_id)`, `sessions(expires_at)`.
- Add CHECK constraints for enum-like text columns: `users.role`, `tasks.status`, `tasks.priority`, `activity_events.event_type`, `notifications.event_type`.
- Author one initial Alembic migration (`0001_initial.py`) capturing all of the above. Hand-edit after autogenerate to ensure index definitions and constraints match the spec.
- Add a migration boot test (ADR 079): empty DB → `alembic upgrade head` → assert schema invariants (table presence, key indexes).
- Wire migrations to run on container startup via the api entrypoint (TDD §8.4); fail the boot if migration errors.

**Deliverables:** A fully-migrated Postgres schema matching TDD §8 and a CI test that proves it boots from empty.

**Definition of done:**
- `make migrate` brings an empty DB to `head` without error.
- The migration test passes in CI.
- All indexes from TDD §17 exist (verified by an introspection query in the test).

**References:** ADRs 033, 034, 035, 062, 079, 084 · TDD §8, §17.1

---

#### Phase B3 — Authentication and Authorization Core

**Goal:** All the auth primitives — password hashing, sessions, CSRF, dependency-injected current user, role and project-access checks, audit log — are in place before any auth-using endpoint is built.

**Tasks:**
- Implement Argon2id password hashing (ADR 048) using `argon2-cffi` with parameters `time_cost=3, memory_cost=65536, parallelism=4`. Helpers `hash_password(plain) -> str` and `verify_password(plain, hash) -> bool`.
- Implement session creation, lookup, and cleanup helpers (ADR 047). Sessions stored in Postgres (ADR 068) with SHA-256-hashed token IDs (TDD §8.2 `sessions`).
- Implement CSRF double-submit (ADR 051): generate `csrf_token` per session; helpers to read cookie + header and compare. Skip for safe methods.
- Implement FastAPI dependencies in `taskflow/auth/dependencies.py`:
  - `get_db()`
  - `current_session()` — reads session cookie, verifies, updates `last_seen_at`, enforces 7-day idle and 30-day absolute (TDD §11.2).
  - `current_user()` — depends on `current_session`.
  - `current_workspace()` — returns the user's workspace (TaskFlow is one-workspace-per-user, PRD §4.1).
  - `require_role(*roles)` — factory that enforces a role floor (PRD §2.1).
  - `require_project_access(project_id_param)` — checks `project_memberships` (or implicit access for owner/admin).
  - `verify_csrf()` — for state-changing requests.
- Implement `taskflow/auth/permissions.py` with a function table mapping every (role, action, project-access) → allowed/denied per PRD §2.1.
- Build the `audit_log` write helper (ADR 084). Synchronous, runs inside the same transaction as the mutation that triggered it.
- Unit tests for the permission table (every cell of role × action × project access combination per PRD §2.1).
- Unit tests for password hashing (verify happy path, wrong password, hash upgrade-readiness).
- Unit tests for CSRF (mismatch, missing header, missing cookie, GET bypass).

**Deliverables:** A fully testable auth stack with no endpoints yet — every dependency that future endpoints will use is in place.

**Definition of done:**
- All permission table unit tests pass.
- CSRF unit tests pass.
- Argon2 hash/verify unit tests pass.
- Session lookup correctly rejects expired, idle-expired, and deleted-user sessions.

**References:** ADRs 010, 047, 048, 050, 051, 068, 084 · PRD §2.1, §4.1 · TDD §7.3, §11

---

#### Phase B4 — Authentication Endpoints

**Goal:** All public auth endpoints exist and produce the correct cookies, audit log entries, and response envelopes.

**Tasks:**
- `POST /api/v1/auth/signup` — atomically creates a workspace + Owner user. Validates email + password rules. Issues session cookies. Audit log: `auth.signup`.
- `POST /api/v1/auth/login` — verifies password, creates session, sets cookies. Audit log: `auth.login.success` / `auth.login.failure`. Rate-limited (deferred wiring; decorator placeholder for E1).
- `POST /api/v1/auth/logout` — deletes session row, clears cookies. Audit log: `auth.logout`.
- `POST /api/v1/auth/password-reset/request` (ADR 049) — no-enumeration response, generates token (1h expiry, single-use), enqueues email via BackgroundTasks (email send wired in D2). Audit log: `auth.password_reset.requested`.
- `POST /api/v1/auth/password-reset/confirm` (ADR 049) — verifies token, updates password hash, revokes all sessions for the user. Audit log: `auth.password_reset.completed` (per ADR 084).
- `GET /api/v1/auth/me` — returns the current user DTO including role and workspace.
- `PATCH /api/v1/auth/me` — update profile fields on the current user (display name only at v1; email is read-only per PRD §20.1). Audit log: `auth.profile.updated`.
- `POST /api/v1/auth/change-password` — authenticated password change (screen inventory §3.11). Verifies current password, hashes and stores new password, revokes all other sessions for the user. Audit log: `auth.password.changed`.
- `DELETE /api/v1/auth/me` — self-account-deletion (PRD §20.2 / screen inventory §5.9). Body includes current password for identity confirmation. Performs in-place anonymization per ADR 065 / TDD §11.7: clears PII, deletes sessions, unassigns tasks. Audit log: `auth.account_deleted`.
- `POST /api/v1/auth/accept-invitation` (PRD §3.3, ADR 011) — takes invitation token + optional new account fields. Adds user to workspace if they exist; creates user otherwise. Marks invitation accepted. Issues session.
- Pydantic DTOs for every request/response (ADR 042). Email validation via `EmailStr`. Password rules: min length, complexity per any constraint adopted (default min 8).
- DTO convention: `CurrentUser` and `UserSummary` (the shared types in screen inventory §8) include `initials` (derived from `display_name`) and `avatar_color` (deterministic hash of user `id`, mapped to one of the six colors in DRD §2.10). Centralized in a single helper so the values are stable across endpoints.
- Integration tests covering: happy path for each endpoint, invalid input (422 with `fields`), wrong password, expired/invalid invitation token, expired/used password reset token, no-enumeration on reset request, session cookie behavior on login, CSRF requirement, change-password revokes other sessions, self-delete anonymization preserves authored content.

**Deliverables:** A signup → login → /me → logout journey works end-to-end via `curl`.

**Definition of done:**
- All integration tests pass.
- Cookies are set with `HttpOnly`, `Secure`, `SameSite=Lax`, correct paths, correct expiries (TDD §11.1).
- Audit log entries exist for every auth-significant event (verified in tests).

**References:** ADRs 011, 047, 048, 049, 084 · PRD §3, §4.2, §20.2 · TDD §11

---

### Part C — Backend Domain

Each Part C phase follows the same pattern: Pydantic DTOs, service layer, endpoints, dependencies (`require_role`, `require_project_access`, `verify_csrf`), audit log entries for state changes, integration tests across roles × project access, OpenAPI types regenerated.

#### Phase C1 — Workspace, Members, Invitations, Labels

**Goal:** Workspace settings, member listing/role-change/removal, invitation send/list/resend, and the workspace-wide label set are fully exposed.

**Tasks:**
- Workspace endpoints: `GET /workspaces/me`, `PATCH /workspaces/me` (Owner/Admin).
- Member endpoints: `GET /workspaces/me/members`, `PATCH /workspaces/me/members/:userId` (role change, Owner/Admin), `DELETE /workspaces/me/members/:userId` (remove, Owner only).
- Member removal flow per ADR 065 / PRD §4.2: anonymize user (`deleted_at`, clear `email`/`name`/`password_hash`), delete sessions, unassign tasks (`UPDATE tasks SET assignee_id = NULL`), audit log.
- Invitation endpoints: `GET /workspaces/me/invitations`, `POST /workspaces/me/invitations` (creates row, generates token, queues email), `POST /workspaces/me/invitations/:id/resend` (regenerates token, queues email, resets expiry).
- Invitation expiry computed from `expires_at`; pending/accepted/expired derived (PRD §3.3).
- Label endpoints: `GET /labels`, `POST /labels` (Owner/Admin), `PATCH /labels/:id`, `DELETE /labels/:id`. Color must be from the fixed palette (DRD §2.9).
- Label deletion cascades to `task_labels` (no soft delete; PRD §7).
- Integration tests: every endpoint × every role × happy + denied; invitation lifecycle (create → expire → resend); member removal asserts task unassignment and session deletion.

**Deliverables:** Workspace administration is fully API-driven; an Admin can manage members, invitations, and labels via API.

**Definition of done:** All integration tests green; audit log captures role changes, removals, label CRUD; OpenAPI types regenerated and committed.

**References:** ADRs 011, 065, 084 · PRD §3.3, §4, §7 · DRD §2.9

---

#### Phase C2 — Projects and Project Access

**Goal:** Project CRUD plus the project-membership model that controls visibility.

**Tasks:**
- Project endpoints: `GET /projects` (only projects the caller has access to), `POST /projects` (Owner/Admin/Member, PRD §5.1), `GET /projects/:id`, `PATCH /projects/:id` (Owner/Admin).
- Project-access endpoints: `GET /projects/:id/access`, `POST /projects/:id/access` (Owner/Admin), `DELETE /projects/:id/access/:userId` (Owner/Admin).
- Service-level helper `assert_project_visible(user, project)` used by the dependency `require_project_access`. Owner/Admin have implicit visibility (PRD §5.2 / TDD §11.5).
- Audit log entries for project create/update, access add/remove.
- Integration tests covering cross-workspace isolation (TDD §8.3): a user in workspace A cannot see / modify projects in workspace B even with a guessed UUID. This is the primary defense against single-tenant logical-isolation risk (ADR 003).

**Deliverables:** Project visibility correctly reflects role and access grants.

**Definition of done:** All integration tests green; cross-workspace isolation tests are present and passing.

**References:** ADRs 003, 084 · PRD §5 · TDD §8.3, §11.5

---

#### Phase C3 — Tasks

**Goal:** Task CRUD, status transitions, label assignments, sort/filter parameters, and FTS column maintenance.

**Tasks:**
- Task endpoints: `GET /projects/:id/tasks` with cursor pagination (ADR 040) and query params for `status[]`, `assignee[]`, `priority[]`, `label[]`, `due` (`overdue|today|this_week|no_due_date`), `include_cancelled` (default false; PRD §6.9), `sort` (`created_at|priority|due_date|assignee`; PRD §6.6 — sort key names match screen inventory §3.5).
- `POST /projects/:id/tasks` (Owner/Admin/Member, PRD §6.1). Defaults: status `backlog`, priority `none`.
- `GET /tasks/:id`, `PATCH /tasks/:id` (Owner/Admin/Member). Title required (non-empty), description Markdown (ADR 014).
- `PATCH /tasks/:id/status` (split for clarity; allows status-only mutations to be small messages and easy to audit).
- Task-label assignment via PATCH (full replacement of label set in one call).
- Last-write-wins semantics (ADR 008); no optimistic concurrency token at this stage.
- Service-layer enforcement of `workspace_id` scoping on every read and write (TDD §8.3).
- Activity-event row for every task lifecycle change (`task.created`, `task.status_changed`, `task.assigned`, `task.unassigned`) per ADR 063. Per ADR 084 these stay out of `audit_log` — that table is reserved for security-sensitive admin actions.
- Integration tests: every endpoint × every role × happy + denied; cancelled-by-default filter behavior; sort behaviors; assignee must have project access; due-date sort places nulls last; cursor pagination consistency.

**Deliverables:** A complete tasks API. The board view's queries are fully serviceable.

**Definition of done:** All integration tests green. Server-side validation rejects an assignee who lacks project access. The `search_vector` column updates on insert and update (verified by FTS query in tests).

**References:** ADRs 008, 014, 040, 041, 042, 062, 084 · PRD §6, §12.2 · TDD §8.2 (`tasks`), §17.1

---

#### Phase C4 — Comments and @Mentions

**Goal:** Comment CRUD on tasks, with server-side @mention extraction for downstream notification dispatch.

**Tasks:**
- `GET /tasks/:id/comments` (paginated chronological).
- `POST /tasks/:id/comments` (Owner/Admin/Member, PRD §11.1). Body is Markdown.
- Comment editing/deletion: author-only per ADR 088. `PATCH /comments/:id` and `DELETE /comments/:id` are restricted to the comment's author; Owner/Admin cannot mutate other users' comments. (Resolves Open Item #1.)
- Server-side @mention parser: extract `@handle` tokens, resolve against workspace members, return resolved mention list as part of the comment DTO. Unknown handles remain plain text (TDD §6.6).
- Activity-event row on `comment.created` per ADR 063. Per ADR 084 these stay out of `audit_log` — comment lifecycle isn't a security event.
- Integration tests: post comment with mentions, verify resolved mentions in response; viewer cannot post; mention of cross-workspace user is dropped; large body handling.

**Deliverables:** Comments are storable, retrievable, and carry a resolved mention list ready for notification dispatch.

**Definition of done:** All integration tests green. The comment DTO includes resolved mentions in a consistent shape.

**References:** ADRs 014, 060 · PRD §11 · TDD §6.6

---

#### Phase C5 — Activity Feed

**Goal:** Activity events are written by services on every relevant mutation and are queryable at workspace and project scope.

**Tasks:**
- Service helper `emit_activity(event_type, actor, subject, metadata, project_id?)` writing to `activity_events` (ADR 063). Called from every relevant service path: task created, status changed, assigned/unassigned, comment created.
- Endpoints: `GET /activity` (workspace-scope, defaults to caller's workspace) and `GET /activity?project_id=...` (project-scope, requires project access). Cursor pagination by `(created_at DESC, id)`.
- Project-access filtering: workspace-scope feed excludes events from projects the caller can't see (TDD §8 join + filter in query).
- Integration tests: emit each event type and assert it appears in the right scope; cross-project visibility is filtered correctly; pagination consistency.

**Deliverables:** Activity is written everywhere it should be, and the feed endpoint serves the dashboard's "Recent Activity" and the project-scope feed.

**Definition of done:** All integration tests green. Performance smoke (<50 ms) is deferred to E3, where seed data (E4) provides representative volume.

**References:** ADR 063 · PRD §13.2, §14 · TDD §8.2 (`activity_events`)

---

#### Phase C6 — Notifications

**Goal:** Notifications are dispatched on the four PRD-defined triggers and are queryable, with an unread badge query that is index-optimized.

**Tasks:**
- Service helper `dispatch_notifications(...)` per ADR 070 invoked from the relevant service paths:
  - Mention in a comment → notify each mentioned user (excluding the actor; PRD §15.1).
  - Task assigned/reassigned → notify the new assignee (excluding actor).
  - Status change on assigned task → notify the assignee (excluding actor).
  - Comment on assigned task → notify the assignee (excluding actor and the mentioned users to avoid double notification).
- Endpoints: `GET /notifications` (paginated, reverse chronological), `POST /notifications/mark-all-read`, `POST /notifications/:id/read`.
- Unread badge query: `COUNT(*) FROM notifications WHERE recipient_id = $1 AND read_at IS NULL` — backed by partial index from B2 (TDD §17.1).
- Integration tests covering every trigger including the self-trigger suppression rule (PRD §15.1).

**Deliverables:** All four notification triggers fire correctly and the badge query is a single index scan.

**Definition of done:** All integration tests green. Self-trigger tests assert no notification row is created.

**References:** ADRs 064, 070 · PRD §15 · TDD §8.2 (`notifications`), §17.1

---

#### Phase C7 — Search

**Goal:** Full-text search across tasks the caller can see, returning ranked results.

**Tasks:**
- `GET /search?q=...` returning ranked task matches (ADR 062).
- Use `websearch_to_tsquery` for safe parsing of arbitrary user input (TDD §12.2).
- Filter by accessible projects (workspace + project-access scoping).
- Result DTO includes task title, project name, and status. Snippet is deferred per PRD §12.1 (revisit post-v1).
- Rank with `ts_rank_cd`. Limit results to ~20.
- Integration tests: matching titles, matching descriptions, exclusion of inaccessible projects, malformed query produces empty result not error, cancelled tasks excluded by default.

**Deliverables:** Search backs the global header search overlay.

**Definition of done:** All integration tests green. Performance smoke (<50 ms) is deferred to E3 with seed data.

**References:** ADR 062 · PRD §12.1 · TDD §8.2 (`tasks.search_vector`)

---

#### Phase C8 — Dashboard Endpoints

**Goal:** The two dashboard data sources — "My tasks" and "Projects with task counts" — are available as scoped endpoints rather than client-side aggregation.

**Tasks:**
- `GET /dashboard/my-tasks` — returns tasks where `assignee_id = current_user`, grouped by project, sorted by due date asc with overdue first (PRD §13.1). Indexed query per `tasks(assignee_id, due_date)` (TDD §17.1).
- `GET /dashboard/projects` — returns projects the caller can see, each with a task-count breakdown by status (PRD §13.3 / DRD §8.3 "Projects").
- Integration tests: empty states, role-aware visibility, status counts correct, overdue ordering.

**Deliverables:** Dashboard data is fetched in two queries, not by composing many task queries client-side.

**Definition of done:** All integration tests green. Endpoints return well-shaped DTOs distinct from raw ORM models (ADR 034).

**References:** ADRs 034, 040 · PRD §13 · TDD §8.2, §17.1

---

### Part D — Backend Real-Time and Async

#### Phase D1 — Real-Time / WebSocket

**Goal:** A working `/ws` endpoint that authenticates with the session cookie, subscribes the client to user/workspace/project channels, and receives events published by services.

**Tasks:**
- Add `broadcaster` dependency, configured with the Postgres backend (ADR 045).
- Implement WebSocket endpoint `/ws` per TDD §10.1: validate session cookie + CSRF query param (ADR 051), subscribe to `user:{id}`, `workspace:{id}`, and `project:{id}` for each accessible project. Re-subscribe on access changes via a control message.
- Implement `publish_event(channel, envelope)` helper used by services after a transaction commits (TDD §10.2). Envelope shape per TDD §10.2.
- Wire publishing into every Part C service that mutates state: `task.created`, `task.updated`, `task.status_changed`, `comment.created`, `notification.created`, `activity` events.
- Reconnect & at-most-once semantics handled by client (TDD §10.4); document expectations.
- Integration tests: open a WS connection in a test, mutate via API, assert the WS receives the event; cross-workspace test asserts no leakage.
- Load test smoke: 50 concurrent connections, mutate, assert receipt within 100 ms.

**Deliverables:** Mutations are broadcast to subscribed clients in real time.

**Definition of done:** Integration WS tests pass; cross-workspace leakage tests pass; CSP-friendly ping/pong frames are configured.

**References:** ADRs 044, 045, 051, 070 · PRD §15.4, §19 · TDD §10

---

#### Phase D2 — Background Jobs and Email

**Goal:** Periodic jobs run inside the FastAPI process; transactional email sends asynchronously after the request returns.

**Tasks:**
- Configure APScheduler `AsyncIOScheduler` to start with the FastAPI app (TDD §7.4 / ADR 069). Jobs:
  - Expire invitations older than 7 days (every 15 minutes).
  - Delete expired sessions (daily 04:00 UTC).
  - Delete expired password-reset tokens (daily 04:00 UTC).
  - `pg_dump` to S3 (daily 03:00 UTC) — implemented as a shell-out in the job; in dev a no-op (ADR 074).
- SES adapter (ADR 067) with two implementations: SES (prod) and SMTP-to-MailHog (dev). Selected by env.
- Email templates (plain text + HTML) for: invitation, password reset.
- Wire `BackgroundTasks` for invitation send and password-reset send (TDD §7.4).
- Tests: scheduler boots; jobs execute (manual trigger); MailHog receives invitation email in dev.

**Deliverables:** Email is sent reliably; scheduled cleanup runs.

**Definition of done:** Manual test sends an invitation, MailHog receives it, recipient can complete the accept-invitation flow.

**References:** ADRs 067, 069, 074 · TDD §7.4, §15.1

---

### Part E — Backend Hardening

#### Phase E1 — Security: Rate Limiting, Headers, Audit Coverage

**Goal:** Sensitive endpoints are rate-limited; nginx security headers are authored; audit log coverage is verified to be complete.

**Tasks:**
- Apply `slowapi` decorators (ADR 052) to: `POST /auth/login` (5/min/IP, 10/min/email), `POST /auth/signup` (3/hr/IP), `POST /auth/password-reset/request` (3/hr/IP, 3/hr/email), `POST /workspaces/me/invitations` (20/hr/workspace). 429 responses follow ADR 043 envelope with `code: "RATE_LIMITED"` and `Retry-After` header.
- Author `infra/nginx/nginx.conf` with the security headers per ADR 083: strict CSP (no `unsafe-inline`/`unsafe-eval`), `frame-ancestors 'none'`, HSTS preload, `Referrer-Policy: strict-origin-when-cross-origin`, `X-Content-Type-Options: nosniff`.
- Author the routing block: `/api/*` → api:8000, `/ws` → api:8000 (with upgrade), everything else → web:80.
- Audit coverage check: walk the audit_log spec (ADR 084) and verify every event type is emitted by some service path. Add tests that drive the path and assert the row.
- Integration tests for rate-limit responses and nginx config (via `nginx -t` in CI).

**Deliverables:** All sensitive endpoints rate-limited; nginx config is production-ready (TLS termination is added in I2 with certbot).

**Definition of done:** Rate-limit tests pass. `nginx -t` passes in CI. Audit-coverage tests pass.

**References:** ADRs 043, 052, 083, 084 · TDD §5.2, §12

---

#### Phase E2 — Observability

**Goal:** Logs are structured, scrubbed of PII, carry request IDs, and emit the metrics that CloudWatch filters will consume.

**Tasks:**
- Request-ID middleware: generate UUIDv7 per request, expose in response header `X-Request-Id`, attach to log context (TDD §13.1).
- Logging middleware: log every request with `path`, `method`, `status`, `duration_ms`, `user_id?`, `workspace_id?`.
- PII scrubbing rules in `structlog` processors: never log email, name, password, comment body, task description (TDD §13.1).
- Auth events logged with stable event names matched by CloudWatch metric filters (TDD §13.2): `auth.login.success`, `auth.login.failure`, etc.
- Periodic gauge emitter for `websocket_connections`.
- `/health` already exists from B1; review and harden.

**Deliverables:** Logs ready for CloudWatch metric filters.

**Definition of done:** Sample log lines verified against the CloudWatch metric-filter regex set; PII-leak tests assert no scrubbed field appears in any log.

**References:** ADRs 075, 076 · TDD §13

---

#### Phase E3 — Backend Test Completion

**Goal:** Bring backend test coverage to the spec floor: every endpoint × every role × every project-access state, plus the cross-cutting integration tests.

**Tasks:**
- Audit endpoint coverage; fill gaps from Parts B–D.
- LISTEN/NOTIFY round-trip integration test (TDD §16.2): publish, assert subscribed consumer receives.
- FTS integration test: insert tasks, assert `websearch_to_tsquery` matches expected subset.
- Migration test (already in B2) re-verified.
- Workspace isolation test sweep: for each workspace-scoped endpoint, assert that user A in workspace 1 cannot affect data in workspace 2 even with a guessed/known UUID.
- Add a coverage report in CI; aim for ≥85% on `services/` and `auth/`.

**Deliverables:** A backend that is provably correct for every documented role × action × scope combination.

**Definition of done:** Coverage report meets target; all listed test categories present and green; CI run time stays under 10 minutes.

**References:** ADR 079 · TDD §16

---

#### Phase E4 — Seed Data

**Goal:** A repeatable, idempotent seed script produces the "Aurora Studio" workspace described in ADR 066.

**Tasks:**
- Implement `apps/api/taskflow/scripts/seed.py` (idempotent — re-running with the same DB is a no-op).
- Workspace "Aurora Studio".
- 5 users covering Owner / Admin / Member / Viewer.
- 3 projects with varied access assignments.
- ~30 tasks exercising every status, priority, label combination, and due-date state (overdue / today / this week / future / none).
- Sample comments with @mentions to drive notifications and activity rows.
- README section documenting the seed credentials.

**Deliverables:** `make seed` populates a working demo instance.

**Definition of done:** After `make seed`, the dashboard, board, list, and search endpoints all return non-empty, varied data via API.

**References:** ADR 066 · TDD §15.3

---

### Part F — Frontend Foundation

#### Phase F1 — Frontend Skeleton

**Goal:** A Vite + React + TypeScript app boots, applies the design tokens, and is ready to host routes.

**Tasks:**
- Vite + React 19 + TypeScript strict (ADRs 027, 029, 030, 031). `apps/web/vite.config.ts`. The frontend toolchain (React 19.2, Vite 8, `@vitejs/plugin-react` 6) was bumped ahead of Phase F1 — see `implementation-status.md` Dependabot Policy block.
- Tailwind v3 (ADR 057) with `tailwind.config.ts` mapping theme keys to CSS custom properties.
- `apps/web/src/styles/tokens.css` — every design token from DRD §2 declared on `:root` exactly per the DRD tables.
- Inter font loaded from Google Fonts (DRD §3.1).
- TanStack Query v5 (ADR 053) with `QueryClientProvider`.
- TanStack Router v1 (ADR 055) with an empty route tree.
- React Hook Form + Zod (ADR 056) added; one shared schema directory.
- `react-intl` (ADR 061) with an `IntlProvider` at the root, English `locales/en.json` seeded with placeholder messages.
- Logical CSS properties enforced via Tailwind utilities (`ms-*`, `me-*`, etc.) per ADR 019.
- Reduced-motion global rule (ADR 025) per TDD §6.5.

**Deliverables:** An empty app shell that loads at `/` with tokens active.

**Definition of done:** `pnpm dev` shows a page styled with the warm-neutral tokens; `prefers-reduced-motion` disables transitions; lighthouse a11y baseline ≥ 90.

**References:** ADRs 019, 022, 023, 025, 027, 029, 030, 031, 053, 054, 055, 056, 057, 061 · DRD §2, §3, §13.2

---

#### Phase F2 — API Client and Type Codegen

**Goal:** TypeScript types and a typed query/mutation client are generated from the backend's OpenAPI schema.

**Tasks:**
- Install `openapi-typescript`. Add `pnpm gen:api` script that fetches the running api's `/api/v1/openapi.json` and writes `packages/api-types/schema.d.ts`.
- Add a CI job `openapi-drift` that regenerates the types and fails the build if the committed file differs (TDD §14.1).
- Build a thin typed `apiClient` in `apps/web/src/api/client.ts` using fetch + cookies, with the CSRF header automatically included on state-changing methods.
- Build typed query hooks helpers (`useApiQuery`, `useApiMutation`) that wrap TanStack Query and use the schema types.
- Smoke test against a running backend: hit `/auth/me` (will 401 without a session — assert the error envelope is parsed correctly).

**Deliverables:** Frontend code can call the backend with full type safety and no hand-written DTOs.

**Definition of done:** Generated types compile; `openapi-drift` CI gate is green; sample typed call to `/auth/me` succeeds with correct types.

**References:** ADRs 042, 043, 053 · TDD §4.1, §6.3, §9.3, §14.1

---

#### Phase F3 — UI Primitives and Storybook

**Goal:** Every Radix-backed component primitive and badge/chip per DRD §7 exists, is themed with tokens, and has Storybook stories.

**Tasks:**
- Install Radix UI primitives (ADR 058) + `class-variance-authority` for variant management (shadcn pattern).
- Add Storybook for component-level testing (also enables `vitest-axe` per ADR 081).
- Build primitives per DRD §7 in `src/components/ui/`:
  - `Button` (Primary, Secondary, Ghost, Destructive variants; sizes; DRD §7.1).
  - `Input`, `Textarea`, `Select` (DRD §7.2).
  - `Avatar` (with deterministic color from user id; DRD §7.3, §2.10).
  - `StatusBadge` (DRD §7.4, colors from §2.6).
  - `LabelChip` (DRD §7.5, colors from §2.9).
  - `PriorityIcon` (DRD §7.6).
  - `DueDate` (DRD §7.7, with overdue/approaching styling).
  - `Toast` system (DRD §7.8).
  - `Dialog` (modal base for §10), `DropdownMenu`, `Tabs`, `Checkbox`, `Tooltip`.
- Lucide icons (ADR 024) integrated; default sizing per DRD §4.2.
- Stories for every primitive covering each variant, each state (default/hover/focus/disabled), and the role-aware variants where applicable.

**Deliverables:** A complete primitive library; Storybook serves as the design-system reference.

**Definition of done:** Storybook runs cleanly; every primitive listed above has at least one story per variant; `vitest-axe` passes on every story.

**References:** ADRs 022, 024, 025, 057, 058, 081 · DRD §2.6, §2.9, §2.10, §4, §7

---

#### Phase F4 — App Shell

**Goal:** The persistent three-zone layout (sidebar / header / content) is in place with empty content slots.

**Tasks:**
- Implement `_shell.tsx` per DRD §6.1. Three zones with the exact pixel dimensions (sidebar 240, header 52).
- Sidebar (DRD §6.3): logo block, primary nav (Dashboard, Notifications), Projects section (header + list with project color dots), bottom section (Settings link + user identity block). Hover/active states per DRD §6.3 styling table.
- Header (DRD §6.4): breadcrumb, search input (260px, ⌘K hint), notification bell (badge), user avatar with dropdown trigger.
- Logo + wordmark per DRD §5.
- Responsive shell behavior per DRD §6.2 / §15: sidebar collapses to icon at tablet (~60px) and becomes hamburger overlay on mobile.
- Add the route tree per screen inventory §3 — empty placeholder components for: `/login`, `/signup`, `/invitations/:token`, `/dashboard`, `/projects/:projectId/board`, `/projects/:projectId/list`, `/projects/:projectId/tasks/:taskId`, `/notifications`, `/settings/{workspace,members,labels,profile}`. `/projects/:projectId` redirects to `/projects/:projectId/board` so a bare project URL still lands on the default view.
- `useCurrentUser` hook backed by `/auth/me`. Unauthenticated routes (`/login`, `/signup`, `/invitations/:token`) are rendered outside the shell.

**Deliverables:** Navigating between routes lands you in the right shell context.

**Definition of done:** Shell renders correctly at desktop / tablet / mobile breakpoints; sidebar active state reflects current route; breadcrumb populates from route data.

**References:** ADRs 005, 009, 055 · DRD §5, §6, §15 · TDD §6.1, §6.2

---

### Part G — Frontend Screens

Each Part G phase reads: build the screen with full state coverage (loading / error / empty / populated), wire to the backend via the typed client, write component tests + axe checks, and confirm against the DRD page spec.

#### Phase G1 — Auth Screens

**Goal:** Login, signup, accept-invitation, and password-reset flows match DRD §8.1, §8.2.

**Tasks:**
- Login screen (DRD §8.1): centered card layout, email/password fields, primary submit, link to signup, password-reset link, inline validation per DRD §18.1.
- Signup screen (DRD §8.1): same shell, fields per PRD §3.1, link to login.
- Accept-invitation screen (DRD §8.2): handles new vs existing user paths and expired-invitation state.
- Password-reset request and confirm screens.
- Form schemas in `forms/schemas/` using Zod (ADR 056).
- Mutation hooks call the backend; on success, hydrate the user cache and navigate.
- All copy per the tone & voice guide.

**Deliverables:** Full unauthenticated journey works against a live backend.

**Definition of done:** Each screen has component + axe tests; cookies are set after successful auth; redirect to dashboard works.

**References:** PRD §3, §20.2 · DRD §8.1, §8.2, §18

---

#### Phase G2 — Dashboard

**Goal:** The dashboard renders My Tasks, Recent Activity, and Projects per DRD §8.3 / PRD §13.

**Tasks:**
- Two-column grid (60/40 desktop) per DRD §8.3.
- "My tasks" section: groups by project, task rows with priority icon / title / status badge / due date.
- "Recent activity" section: avatar + sentence-style entries with relative timestamps; teal task links.
- "Projects" section: project cards with color dot, name, status-count summary.
- Empty states per DRD §16 (role-aware).
- First-run prompts: Owner sees "Create your first project"; invited user sees brief welcome (PRD §3.4 / DRD §16). Visibility derived from workspace state (project count, user creation date relative to workspace creation). The "Invite team members" prompt is owned by Phase H2 since it surfaces in the sidebar/settings rather than the dashboard.
- Build the Create Project modal (DRD §10.1, screen inventory §5.1). Reused by the sidebar `+` action, the dashboard "No projects yet" empty state, and the Owner first-run prompt.
- Wire to `/dashboard/my-tasks`, `/dashboard/projects`, `/activity` endpoints.

**Deliverables:** A real dashboard against real data.

**Definition of done:** Component tests cover empty / populated / role-variant states; axe clean.

**References:** PRD §3.4, §13 · DRD §8.3, §16

---

#### Phase G3 — Board View

**Goal:** Drag-and-drop board view per DRD §8.4 / PRD §8 with optimistic status updates.

**Tasks:**
- Sub-navigation bar (DRD §8.4 / screen inventory §3.5): view toggle, filter button, active filter chips, "Clear all" link, sort dropdown, project settings icon (Owner/Admin only), Create-task button (role-gated).
- Filter chip bar shown when filters active (DRD §8.4).
- Five columns (Backlog / To Do / In Progress / In Review / Done) — Cancelled hidden by default; filter to show.
- Task cards per DRD §8.4: title, labels (max 3 + overflow), meta row (priority / due / comment count / assignee).
- Drag-and-drop with `@dnd-kit/core` (ADR 059) — desktop only. Drop target column highlights with `--primary-light`.
- Optimistic UI for the status mutation per ADR 046 (`onMutate` / `onError` / `onSettled`); on error, snap back and toast.
- URL-driven filter and sort state (shared with list view).
- Wire to `/projects/:id/tasks` with the right query params.
- Build the Project Settings modal (DRD §10.2 / screen inventory §5.2): Details tab (name, description, save) and Access tab (member list with add/remove, backed by the project-access endpoints from Phase C2). Triggered from the project settings icon.
- Mobile: columns stack; status changes via dropdown only (no DnD; DRD §15.3).

**Deliverables:** Board view fully usable; drag-and-drop with real-time fan-out (real-time wired in H1).

**Definition of done:** Component tests cover sort, filter, drag (with mock dnd context), error rollback; axe clean.

**References:** ADRs 046, 059 · PRD §6, §8, §12.2 · DRD §8.4, §15

---

#### Phase G4 — List View

**Goal:** Tabular alternative view per DRD §8.5 / PRD §9.

**Tasks:**
- Sortable columns: title, status, assignee, priority, due date, labels (labels not sortable).
- Inline status dropdown per row (Owner/Admin/Member).
- Shares filter/sort URL state with board view; preserved on toggle.
- Mobile: horizontal scroll or stacked cards per DRD §15.3.

**Deliverables:** List view fully usable.

**Definition of done:** Component tests cover sort interactions, status change, role gating; axe clean.

**References:** PRD §9 · DRD §8.5, §15.3

---

#### Phase G5 — Task Detail Panel

**Goal:** Side-panel task view with property editing, Markdown description, and comments (DRD §9.1 / PRD §10).

**Tasks:**
- Panel route at `/projects/:projectId/tasks/:taskId` per TDD §6.2; backdrop click / Esc / × all close (DRD §12.4).
- Slide-in animation 200ms ease-out; respects reduced motion (DRD §9.1, §13).
- Header: title (inline editable), status dropdown, close.
- Properties: status, assignee, priority, due date, labels — each with inline editor; viewer sees read-only.
- Description: rendered Markdown by default; click to edit (Markdown textarea); save on blur or explicit save.
- Markdown rendering pipeline per ADR 060 (TDD §6.6): `react-markdown` + `remark-gfm` + `rehype-sanitize` (strict allowlist). Links open with `rel="noopener noreferrer nofollow"`.
- Comments section: chronological list, new comment input at bottom (Owner/Admin/Member).
- @mention autocomplete in the comment input and description editor (DRD §11.4) — typeahead against workspace members.
- Wire to `/tasks/:id`, `/tasks/:id/comments`.
- Mobile: full-screen panel.

**Deliverables:** Complete task detail experience.

**Definition of done:** Component tests cover the editor toggles, mention autocomplete, viewer read-only state, panel dismissal; axe clean.

**References:** ADRs 014, 046, 060 · PRD §10, §11 · DRD §9, §11.4, §12.4, §15

---

#### Phase G6 — Notifications Page and Badge

**Goal:** Notifications page per DRD §8.6, badge in the global header per DRD §6.4.

**Tasks:**
- Notifications page: reverse chronological list, unread style (`--primary-light` background tint), event description, task link, project, relative timestamp, "Mark all as read".
- Click marks-as-read and navigates to the task.
- Badge in header bound to the unread-count query.
- Empty state per DRD §16 ("You're all caught up.").

**Deliverables:** Notifications work end-to-end (real-time arrival wired in H1).

**Definition of done:** Component tests cover read/unread styling, mark-all behavior, navigation; axe clean.

**References:** PRD §15 · DRD §6.4, §8.6, §16

---

#### Phase G7 — Search Overlay

**Goal:** Global search dropdown triggered by input focus or ⌘K (DRD §11.1 / PRD §12.1).

**Tasks:**
- Search input in header; ⌘K / Ctrl+K opens it.
- Dropdown below the input: up to ~8 results with title (matched text highlighted), project, status badge.
- Keyboard nav (arrows, Enter, Esc).
- Wire to `/search?q=...`; debounce input.
- "No tasks match your search." per DRD §16.

**Deliverables:** Full search experience.

**Definition of done:** Component tests cover keyboard nav, debounce, empty results, navigation; axe clean.

**References:** PRD §12.1 · DRD §11.1, §16

---

#### Phase G8 — Settings (Workspace, Members, Labels, Profile)

**Goal:** Settings sub-pages per DRD §8.7–§8.10 / PRD §4, §7, §20.

**Tasks:**
- Settings layout with sub-navigation (sidebar tabs or horizontal tabs per DRD §8.7).
- Workspace tab (DRD §8.7): name input + Save (Owner/Admin only; others redirected).
- Members tab (DRD §8.8): member table (avatar, name, email, role dropdown, remove button); invitation table (email, role, status badge, sent date, resend); "Invite member" modal (DRD §10.4); "Remove member" confirmation modal (DRD §10.5).
- Labels tab (DRD §8.9 / §10.6 / §10.7): label list with edit/delete; create-label modal with palette swatches; delete-label confirmation modal.
- Profile tab (DRD §8.10 / screen inventory §3.11): display name save (`PATCH /auth/me`), email read-only display, change-password section (`POST /auth/change-password`, screen inventory §3.11), danger-zone delete-account button opening the Delete Account modal (DRD §10.8 / screen inventory §5.9, calls `DELETE /auth/me`).
- Last-used view per project remembered in `localStorage` (PRD §9.3) — placed here as the natural place to declare it.

**Deliverables:** Full settings surface across all roles.

**Definition of done:** Component tests cover each tab, role gating, all modals; axe clean.

**References:** PRD §4, §7, §20 · DRD §8.7–§8.10, §10.4–§10.8

---

### Part H — Frontend Cross-Cutting

#### Phase H1 — Real-Time Client Bridge

**Goal:** WebSocket client connects on login, dispatches inbound events into TanStack Query cache updates per TDD §6.3 / §10.3.

**Tasks:**
- Connect to `wss://{host}/ws` after `/auth/me` resolves; carry CSRF token as query param.
- Single `realtimeDispatcher` translating inbound envelopes:
  - `task.updated` → `setQueryData(['task', id], task)` + invalidate board queries for project.
  - `task.created` → invalidate `['project', pid, 'tasks']`.
  - `comment.created` → invalidate `['task', taskId, 'comments']`.
  - `notification` → prepend to `['notifications']` + bump badge.
  - `activity` → prepend to `['activity', scope]`.
- Reconnect with exponential backoff capped at 30s, jittered (TDD §10.4). On reconnect, invalidate all queries.
- Surface a discreet "Reconnecting…" indicator; auto-clear on resume.
- `aria-live` announcement for relevant cross-page events (PRD §16.2 / DRD §14.3).

**Deliverables:** Real-time UX matches PRD §19.

**Definition of done:** Two-browser-context manual test: user A moves a task, user B sees the move within 1 second.

**References:** ADRs 044, 045 · PRD §15.4, §19 · TDD §6.3, §10

---

#### Phase H2 — Empty States and First-Run

**Goal:** Every empty state and first-run prompt described in DRD §16 / PRD §3.4–§3.5 is implemented.

**Tasks:**
- Audit all screens against the DRD §16 table; add or correct empty-state components.
- Implement first-run prompts (PRD §3.4 / DRD §16):
  - Owner — "Create your first project" prompt on the dashboard while the workspace has zero projects (uses the Create Project modal from Phase G2).
  - Owner — "Invite team members" prompt in the sidebar/settings until at least one invitation has been sent (uses the Invite Member modal from Phase G8).
  - Invited user — brief welcome message on the dashboard until the user has at least one assignment or one activity entry attributable to them.
- Visibility derived from current workspace state on the client; no backend "first-run" flag required.
- Confirm role-aware copy and CTAs.

**Deliverables:** Empty states are consistent and on-brand.

**Definition of done:** Visual review against DRD §16 passes; component tests assert each state.

**References:** PRD §3.4, §3.5 · DRD §16

---

#### Phase H3 — Toasts, Errors, Confirmations

**Goal:** Global toast system and destructive confirmation pattern in place per DRD §7.8 / §18.

**Tasks:**
- Global Zustand store for toasts; `useToast` hook (TDD §6.3).
- Toast styling per DRD §7.8 (bottom-right, 5s auto-dismiss, success icon, fade up, reduced motion).
- Mutation error handler standardizes "Couldn't save your changes. Please try again." style copy where appropriate.
- Destructive confirmation modal pattern (DRD §18.3) used for: Remove member, Delete account, Delete label.

**Deliverables:** Consistent feedback for async actions.

**Definition of done:** Component tests for toast lifecycle and confirmation modals.

**References:** DRD §7.8, §18

---

#### Phase H4 — Accessibility Pass

**Goal:** WCAG 2.1 AA verified across the application.

**Tasks:**
- Keyboard sweep: every interactive element reachable; logical tab order; focus visible (`--primary` + `--primary-ring`).
- ARIA: `role="dialog"` + `aria-modal` on modals; `aria-expanded` on dropdown triggers; `aria-label` on icon-only buttons; `aria-live="polite"` on real-time announcement region.
- Color-contrast verification spot checks against tokens (DRD §14.1).
- Reduced-motion verification across all animated interactions (DRD §13.2).
- Manual screen-reader pass (VoiceOver) over the critical journeys.

**Deliverables:** A passing accessibility audit.

**Definition of done:** Page-level axe checks clean; keyboard-only journey for the E2E happy-path completes.

**References:** ADR 017, 081 · PRD §16 · DRD §14

---

#### Phase H5 — Frontend Test Completion

**Goal:** Vitest coverage on hooks, primitives, and domain components reaches the spec floor.

**Tasks:**
- Component tests for every domain component used by Parts G screens.
- Hook tests for permission derivations and form schemas.
- Add coverage report; aim for ≥80% on `components/` and `features/`.
- `vitest-axe` runs on every component test.

**Deliverables:** A frontend test base that prevents regressions during real-time and empty-state revisions.

**Definition of done:** Coverage report meets target; all tests green; CI runtime under 5 minutes for the frontend job.

**References:** ADRs 079, 081 · TDD §16

---

### Part I — E2E, Infrastructure, Deployment

#### Phase I1 — End-to-End Test Suite

**Goal:** Playwright journeys per ADR 080 / TDD §16.3 pass against `docker compose up`.

**Tasks:**
- Playwright config with axe checks via `@axe-core/playwright`.
- Journeys:
  1. Sign-up → create workspace → create first project (Owner).
  2. Accept invitation (new user).
  3. Create task → drag to In Progress → add comment with @mention → mark Done.
  4. Two browser contexts: user A moves a task; user B sees it without refresh.
  5. @mention notification: user B's badge increments in real time.
  6. Search, filter, empty states.
- Add `e2e` job to CI (TDD §14.1).

**Deliverables:** Acceptance suite that proves the application works end-to-end.

**Definition of done:** All journeys green; axe checks green on every visited page; CI job runtime under 15 minutes.

**References:** ADRs 080, 081 · TDD §16.3

---

#### Phase I2 — Infrastructure (CloudFormation)

**Goal:** All AWS resources provisioned via CloudFormation per TDD §5.

**Tasks:**
- Author stacks in `infra/cloudformation/`:
  - `network.yml` — VPC, public subnet, IGW, route table, security group.
  - `compute.yml` — EC2 `t4g.small`, Elastic IP, IAM instance profile, user-data installing Docker + CloudWatch Agent.
  - `container-registry.yml` — ECR repos `taskflow/api`, `taskflow/web` with lifecycle policy.
  - `storage.yml` — S3 buckets for backups (SSE-S3, 30-day lifecycle) and source maps.
  - `parameters.yml` — SSM Parameter Store SecureString placeholders under `/taskflow/prod/*`.
  - `email.yml` — SES verified domain identity, DKIM records.
  - `monitoring.yml` — CloudWatch log groups, metric filters, alarms (per TDD §13.3), SNS topic `taskflow-alerts`.
  - `dns.yml` — Route 53 zone, A record → Elastic IP, MX/TXT for SES, ACM cert (provisioned for future).
  - `iam.yml` — OIDC provider for GitHub Actions, `taskflow-deploy-role` with narrow permissions.
- Author `infra/ec2/user-data.sh` per TDD §5.1.
- Author `docker-compose.prod.yml` with nginx + api + web + db + certbot.
- Wire certbot for Let's Encrypt issuance/renewal (ADR 085 / TDD §5.4).
- Validate templates via `cfn-lint` in CI.

**Deliverables:** Infrastructure deployable from clean account.

**Definition of done:** All stacks deploy cleanly to a staging-style sandbox account; `cfn-lint` clean in CI.

**References:** ADRs 036, 037, 038, 067, 071, 073, 074, 077, 083, 085, 087 · TDD §5

---

#### Phase I3 — CD Pipeline

**Goal:** Push to `main` triggers a full deploy.

**Tasks:**
- Author `.github/workflows/deploy.yml` per TDD §14.2:
  1. Assume `taskflow-deploy-role` via OIDC.
  2. Build `linux/arm64` images, tag with commit SHA, push to ECR.
  3. `aws cloudformation deploy` for each changed stack.
  4. `aws ssm send-command` to run `alembic upgrade head` on the EC2.
  5. `aws ssm send-command` to run `docker compose pull && docker compose up -d --remove-orphans`.
  6. Smoke check `/health` from the workflow; fail on non-200.
- Document rollback procedure (TDD §14.4) in the runbook.

**Deliverables:** End-to-end automated deploy.

**Definition of done:** A trivial change merged to `main` reaches the EC2 host and the smoke check passes.

**References:** ADRs 071, 073, 087 · TDD §14

---

#### Phase I4 — Production Cutover

**Goal:** First production deploy, DNS cut, TLS active, smoke verified.

**Tasks:**
- Set all SSM Parameter Store values for production (DB password, session secret, SES creds, etc.) out-of-band.
- Run the deploy workflow.
- Verify Let's Encrypt certificate issuance and HTTPS reachability.
- Cut Route 53 A record to the Elastic IP.
- Run the seed script in production (or skip if a real workspace will be created on first signup).
- Manual smoke: signup, create project, create task, invite a second user, see real-time updates.

**Deliverables:** TaskFlow is live at the production domain.

**Definition of done:** Manual smoke passes; HTTPS scoring (SSL Labs) ≥ A; security headers (Mozilla Observatory) score ≥ A.

**References:** ADRs 077, 083, 085 · TDD §5.4

---

#### Phase I5 — Monitoring and Alarm Verification

**Goal:** Every CloudWatch alarm in TDD §13.3 fires correctly and routes to email.

**Tasks:**
- Subscribe operator email to `taskflow-alerts` SNS topic.
- Synthesize each alarm condition (induce a failing health check, generate 5xx via a feature-flagged test endpoint, etc.) and verify the email arrives.
- Verify CloudWatch log groups receive logs from all three containers.
- Confirm metric filter regex matches actual log lines (cross-check with E2 work).

**Deliverables:** Operational readiness.

**Definition of done:** Each alarm verified at least once; runbook updated.

**References:** ADRs 075, 076, 077 · TDD §13

---

#### Phase I6 — Final Acceptance and Documentation

**Goal:** Walk the PRD top to bottom against the live system and confirm no gap.

**Tasks:**
- Acceptance walkthrough: every PRD section, every DRD page spec, every empty state.
- Update `README.md` with run, deploy, and seed instructions.
- Update `docs/planning/implementation-status.md` to reflect 100% completion.
- Author a short release note summarizing what shipped.

**Deliverables:** A demonstrable, documented v1.

**Definition of done:** Acceptance walkthrough produces no defects above "trivial."

**References:** All requirements documents.

---

## 5. Cross-Cutting Standards

These apply across every phase. They are not separate phases.

- **Lint and typecheck.** No phase ships with red `make lint` or `make typecheck`.
- **Tests.** Every backend phase ends with integration tests for new endpoints across roles × project access. Every frontend phase ends with component tests + axe checks.
- **Audit log.** Every state-changing service path writes an `audit_log` row inside the same transaction.
- **Real-time fan-out.** Every state-changing service path that affects shared views publishes the corresponding event after commit.
- **Workspace scoping.** Every service-layer DB access filters by `workspace_id`. PR review explicitly checks for this.
- **OpenAPI sync.** Every backend phase that adds or changes an endpoint regenerates `packages/api-types/schema.d.ts`. The `openapi-drift` CI gate enforces this from F2 onward.
- **Tone & voice.** All user-facing copy follows `docs/design/tone-and-voice-guide.md`.
- **Accessibility.** No frontend component ships without an axe check.
- **Documentation in code.** Comments only when *why* is non-obvious; no narration of what.

---

## 6. Specification Coverage Validation

This section is the result of the comparison step requested in the build instructions. It maps every PRD section, every DRD section, and every ADR to the phase that delivers it. Where a gap or open item was found, the plan above has been adjusted; remaining open items are listed at the end.

### 6.1 PRD coverage

| PRD section | Delivered by |
|-------------|--------------|
| §2 Roles & Permissions | B3 (permission table), B4 (auth endpoints), enforced throughout C |
| §3.1 Sign Up | B4, G1 |
| §3.2 Log In | B4, G1 |
| §3.3 Invitations | C1, G1, G8 |
| §3.4 First-Run | H2 |
| §3.5 Empty States | H2 |
| §4.1 Workspace Settings | C1, G8 |
| §4.2 Member Management | C1 (incl. removal/anonymization), G8 |
| §5 Projects | C2, G3 (board), G4 (list), G8 (project access in settings) |
| §6 Tasks | C3, G3, G4, G5 |
| §7 Labels | C1, G8 |
| §8 Board View | G3 |
| §9 List View | G4 |
| §10 Task Detail Panel | G5 |
| §11 Comments | C4, G5 |
| §12.1 Global Search | C7, G7 |
| §12.2 Project Filters | C3 (server-side filter params), G3, G4 |
| §13 Dashboard | C8, G2 |
| §14 Activity Feed | C5, G2 (dashboard feed); project-scope feed surfaced via the project page (see Open Item below) |
| §15 Notifications | C6, G6, H1 |
| §16 Accessibility | F3 (per-component), H4 (system-wide) |
| §17 Responsive | F4, G3, G4, G5 |
| §18 i18n | F1 |
| §19 Real-Time | D1, H1 |
| §20 Account & Data Management | B4, C1, G8 |
| §21 Out of Scope | not built; noted |

### 6.2 DRD coverage

| DRD section | Delivered by |
|-------------|--------------|
| §2 Tokens | F1 (`tokens.css`) |
| §3 Typography | F1 |
| §4 Iconography | F3 |
| §5 Logo | F1, F4 |
| §6 Layout / Sidebar / Header | F4 |
| §7 Components | F3 |
| §8.1 Login / §8.2 Accept Invitation | G1 |
| §8.3 Dashboard | G2 |
| §8.4 Board View | G3 |
| §8.5 List View | G4 |
| §8.6 Notifications | G6 |
| §8.7–§8.10 Settings | G8 |
| §9 Task Detail Panel | G5 |
| §10 Modals | F3 (base), G8 (settings modals), G3 (create task), G2/G8 (create project) |
| §11.1 Search Dropdown | G7 |
| §11.2 User Menu | F4 |
| §11.3 Filter Dropdowns | G3 |
| §11.4 @Mention Autocomplete | G5 |
| §12 Interaction Patterns | G3, G4, H1 |
| §13 Animation & Motion | F1 (reduced-motion), per-component in F3/G* |
| §14 Accessibility | H4 |
| §15 Responsive | F4 (shell), G3 (board mobile stack), G5 (panel full-screen) |
| §16 Empty States & First-Run | H2 |
| §17 i18n | F1 |
| §18 Errors & Confirmations | H3, F3 (modal patterns), G8 (destructive confirmations) |

### 6.3 ADR coverage

All 87 ADRs map to at least one phase. Spot-checks of the less-obvious ones:

- ADR 003 (single-tenant) → enforced via `workspace_id` filtering across C; cross-workspace isolation tests in C2 and E3.
- ADR 008 (last-write-wins) → C3.
- ADR 011 (account onboarding) → B4 (accept-invitation), C1 (invitation issuance).
- ADR 022 (design token layer) → F1.
- ADR 042 (request/response validation) → B1 + every C phase.
- ADR 046 (optimistic UI policy — drag only) → G3.
- ADR 050 (auth library: none) → B3 (custom session implementation).
- ADR 060 (Markdown render & sanitize) → G5 (and `rehype-sanitize` strict allowlist enforced there).
- ADR 062 (FTS implementation) → B2 (column + index), C3 (maintenance), C7 (endpoint).
- ADR 065 (account deletion / anonymization) → B4 (self-delete), C1 (Owner-removes-member).
- ADR 068 (cache/session store: Postgres-only) → B3.
- ADR 069 (background job system) → D2.
- ADR 070 (notification dispatch architecture) → C6 + D1 (publish on commit).
- ADR 074 (backup & DR) → D2 (`pg_dump` job), I2 (S3 bucket).
- ADR 084 (audit logging scope) → B3 (helper) + every state-changing service path; coverage check in E1.
- ADR 087 (IaC) → I2.

### 6.4 Open items found during validation

These are spec gaps or ambiguities surfaced while building the plan. Each has a default decision baked into the plan above; any of them could become an ADR or PRD revision before its phase ships.

1. **Comment edit/delete (PRD §11.3).** PRD defers to implementation. Plan default (Phase C4): `PATCH` and `DELETE` allowed for the comment author only. Recommend recording this as a new ADR before C4 ships.
2. **Email change (PRD §20.1).** PRD defers to implementation. Plan default (Phase G8): not exposed in the profile UI for v1. Recommend a one-line note in the PRD to confirm.
3. **Last-used view per project (PRD §9.3).** TDD does not specify storage. Plan default (Phase G8): `localStorage`, no backend persistence.
4. **Project activity feed surface (PRD §14.2).** DRD does not call out a dedicated UI panel for the project-scope feed. Plan default: surface as a side panel on the project page reachable from the sub-nav. Confirm with design before G3 ships.
5. **First-run prompt logic (PRD §3.4).** No backend "first-run" flag is specified. Plan default (Phase H2): derive from workspace state — Owner sees the prompt while project count is 0; invited user sees the welcome until they have any assignment or activity.

None of these change the architecture or affect another phase's scope. They are tracked in the implementation-status file as items to confirm before their consuming phase begins.

### 6.5 Screen Inventory Consistency

A pass over `screen-inventory.md` after the initial draft surfaced several items that have been reconciled into this version of the plan. The screen inventory is the design contract for what gets built; where it disagreed with the TDD on incidental details, the plan now follows the screen inventory.

| # | Item | Source | Resolution in plan |
|---|------|--------|--------------------|
| 1 | Accept-invitation route | Screen inventory §3.3 specifies `/invitations/:token`; TDD §6.2 had `/accept-invite` | Phase F4 route tree updated to `/invitations/:token` |
| 2 | Project view route | Screen inventory §3.5 specifies `/projects/:projectId/board`; TDD §6.2 used `/projects/:projectId` as default | Phase F4 uses `/projects/:projectId/board`; bare `/projects/:projectId` redirects there |
| 3 | Authenticated change-password endpoint | Screen inventory §3.11 specifies `ChangePasswordRequest { currentPassword, newPassword }`; TDD §9.4 listed only password-reset endpoints | Phase B4 adds `POST /auth/change-password` with session revocation |
| 4 | Display-name update endpoint | Screen inventory §3.11 specifies a Save action on the profile page | Phase B4 adds `PATCH /auth/me` |
| 5 | Self-account-deletion endpoint | Screen inventory §5.9 (Delete Account modal) requires a password to confirm identity; TDD §11.7 describes the flow but lists no endpoint | Phase B4 adds `DELETE /auth/me` performing the in-place anonymization per ADR 065 |
| 6 | Project Settings modal | Screen inventory §5.2 defines the modal accessed from the project sub-nav, with Details and Access tabs | Phase G3 builds the modal; the Access tab uses the project-access endpoints already in Phase C2 |
| 7 | Project sub-nav elements | Screen inventory §3.5 lists active filter chips, "Clear all" link, and Project settings icon — earlier draft only mentioned filter chips | Phase G3 sub-nav task updated to include all elements |
| 8 | Create Project modal as a named deliverable | Screen inventory §5.1 defines the modal triggered from sidebar, dashboard empty state, and first-run prompt | Phase G2 explicitly builds the modal; Phase F4 (sidebar) and Phase H2 (first-run) reference it |
| 9 | First-run "Invite team members" prompt | Screen inventory §5.4 references this prompt as a trigger for the Invite Member modal | Phase H2 task list now enumerates both Owner first-run prompts |
| 10 | `UserSummary` / `CurrentUser` shape | Screen inventory §8 includes `initials` and `avatarColor` on shared user types | Phase B4 declares the DTO convention: backend computes `initials` from `display_name` and `avatar_color` deterministically from `id` (DRD §2.10 palette) |

**Items not reconciled (intentional):** The screen inventory's `LoginResponse` and `SignUpResponse` show a `token` field. The plan continues to use cookie-based session auth per ADR 047 / TDD §11 — the response carries only the `CurrentUser` DTO. This is treated as a stale field in the screen inventory rather than a contradicting decision; the screen inventory should be revised to drop the `token` field at the next opportunity.

---

## 7. Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Backend-first means no clickable UI for weeks. Design changes after F1 cause backend revision. | The DRD and `mockup.html` are the design contract. Any design change between now and F1 must be captured in an updated DRD section before it affects code. |
| OpenAPI codegen catches type drift but not semantic drift. | Integration tests (E3) cover every endpoint × role × scope combination, including the negative cases that catch semantic mistakes. |
| Postgres `LISTEN/NOTIFY` correctness is hard to verify locally. | D1 includes a round-trip integration test; I1 includes a two-context Playwright test that exercises the full path. |
| Single EC2 host has no failover. | Documented as accepted risk in TDD §18.2. RTO ~1h via CloudFormation replacement. Out of scope to mitigate further for v1. |
| Pydantic ↔ Zod drift on shared validation. | Validation rules for critical fields (email, password, title length) are duplicated in tests both server-side (pytest) and client-side (Vitest). Review discipline covers the rest. |
| Long backend stretch may discover schema changes that ripple through done work. | Each Part C phase ships with migrations. Schema changes are additive where possible; integration tests catch regressions. |
| Frontend phases are downstream of backend completion. A delay in backend pushes the frontend critical path. | The codegen contract means frontend foundation work (F1, F3) can begin against a partial schema. Foundation phases F1–F3 do not depend on Part C completeness. |

---

## 8. Reference Documents

| Document | Location |
|----------|----------|
| Implementation Status Tracker | [./implementation-status.md](./implementation-status.md) |
| Business Requirements Document | [../business/business-requirements-document.md](../business/business-requirements-document.md) |
| Product Requirements Document | [../product/product-requirements-document.md](../product/product-requirements-document.md) |
| Design Requirements Document | [../design/design-requirements-document.md](../design/design-requirements-document.md) |
| Technical Design Document | [../technical/technical-design-document.md](../technical/technical-design-document.md) |
| Tone & Voice Guide | [../design/tone-and-voice-guide.md](../design/tone-and-voice-guide.md) |
| Screen Inventory | [../design/screen-inventory.md](../design/screen-inventory.md) |
| Architectural Decision Records | [../technical/decisions/INDEX.md](../technical/decisions/INDEX.md) |
| Design Decision Records | [../design/decisions/INDEX.md](../design/decisions/INDEX.md) |
| Product Decision Records | [../product/decisions/INDEX.md](../product/decisions/INDEX.md) |
| Business Decision Records | [../business/decisions/INDEX.md](../business/decisions/INDEX.md) |
