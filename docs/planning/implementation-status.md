# TaskFlow — Implementation Status

**Last Updated:** 2026-05-09
**Current Phase:** Phase C1 — Workspace, Members, Invitations, Labels (next)
**Plan:** [implementation-plan.md](./implementation-plan.md)

---

## How to Use This File

This file mirrors the phases and tasks defined in `implementation-plan.md`. As work proceeds:

- Update each task's checkbox as it is completed.
- Update each phase's status header (`Not started` → `In progress` → `Complete` / `Blocked`).
- Update the **Last Updated**, **Current Phase**, and the **Progress Summary** table at the top of each session.
- For blocked phases, note the blocker on the phase line (e.g., `[!] Blocked — waiting on X`).
- Open Items from §6.4 of the plan are tracked at the bottom — confirm each one before its consuming phase begins.

Refer to the implementation plan for the goal, definition of done, and references for each phase.

---

## Status Legend

| Marker | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Complete |
| `[!]` | Blocked |

---

## Progress Summary

| Part | Theme | Phases | Complete | In Progress | Blocked |
|------|-------|--------|----------|-------------|---------|
| A | Foundation | 1 | 1 | 0 | 0 |
| B | Backend Core | 4 | 4 | 0 | 0 |
| C | Backend Domain | 8 | 0 | 0 | 0 |
| D | Backend Real-Time & Async | 2 | 0 | 0 | 0 |
| E | Backend Hardening | 4 | 0 | 0 | 0 |
| F | Frontend Foundation | 4 | 0 | 0 | 0 |
| G | Frontend Screens | 8 | 0 | 0 | 0 |
| H | Frontend Cross-Cutting | 5 | 0 | 0 | 0 |
| I | E2E, Infra, Deploy | 6 | 0 | 0 | 0 |
| **Total** | | **42** | **5** | **0** | **0** |

---

## Phase Status

### Part A — Foundation

#### Phase 0 — Project Foundation `[x] Complete`
- [x] Initialize pnpm workspaces monorepo with Turborepo
- [x] Create directory layout (apps, packages, infra, .github)
- [x] Add `pnpm-workspace.yaml`, `turbo.json`, root `package.json`, `Makefile`
- [x] Configure Biome (TS/JS) and Ruff (Python)
- [x] Set up Python 3.12+ with `pyproject.toml`
- [x] Author `docker-compose.yml` (dev), `.test.yml`, `.prod.yml` placeholder
- [x] Author `apps/web/Dockerfile` and `apps/api/Dockerfile` (arm64 stubs)
- [x] Add MailHog to dev compose
- [x] Author `.env.example`
- [x] GitHub Actions `ci.yml` with `lint` and `typecheck` jobs
- [x] Configure Dependabot and CodeQL
- [x] Configure pre-commit hooks
- [x] Root `README.md` with quickstart

---

### Part B — Backend Core

#### Phase B1 — Backend Skeleton `[x] Complete`
- [x] Add FastAPI + Uvicorn to `apps/api`; main.py entry point
- [x] Implement `settings.py` via `pydantic-settings`
- [x] Implement async SQLAlchemy session in `db/session.py`
- [x] Configure Alembic with `alembic.ini` and `env.py`
- [x] Implement global error contract in `errors.py` (per ADR 043)
- [x] Configure structured logging with `structlog` + request-id middleware
- [x] Implement `GET /health` (200 if Postgres reachable)
- [x] Wire `/api/v1` prefix and empty router
- [x] Expose `/api/v1/openapi.json`
- [x] Add `mypy` to CI typecheck job

#### Phase B2 — Database Schema and Migrations `[x] Complete`
- [x] SQLAlchemy ORM models for all 14 tables (TDD §8.2)
- [x] UUIDv7 primary keys, `created_at`/`updated_at` columns
- [x] Partial unique index on `users(workspace_id, lower(email)) WHERE deleted_at IS NULL`
- [x] `tasks.search_vector` generated column + GIN index
- [x] All hot-path indexes (TDD §17.1)
- [x] CHECK constraints for enum-like text columns
- [x] Initial Alembic migration `0001_initial.py`
- [x] Migration boot test (empty → head → assert schema)
- [x] Migrations run on container startup

#### Phase B3 — Authentication and Authorization Core `[x] Complete`
- [x] Argon2id password hashing (`hash_password`, `verify_password`)
- [x] Session creation/lookup/cleanup helpers
- [x] CSRF double-submit helpers
- [x] FastAPI dependencies: `get_db`, `current_session`, `current_user`, `current_workspace`, `require_role`, `require_project_access`, `verify_csrf`
- [x] Permission table in `auth/permissions.py`
- [x] `audit_log` write helper (synchronous, in-transaction)
- [x] Unit tests for permission table (every role × action × project-access cell)
- [x] Unit tests for password hashing
- [x] Unit tests for CSRF (mismatch, missing, GET bypass)

#### Phase B4 — Authentication Endpoints `[x] Complete`
- [x] `POST /auth/signup` (creates workspace + Owner)
- [x] `POST /auth/login` (sets cookies, audit log)
- [x] `POST /auth/logout`
- [x] `POST /auth/password-reset/request` (no enumeration)
- [x] `POST /auth/password-reset/confirm` (revokes sessions)
- [x] `GET /auth/me`
- [x] `PATCH /auth/me` (display name only; email read-only per PRD §20.1)
- [x] `POST /auth/change-password` (verify current, hash new, revoke other sessions)
- [x] `DELETE /auth/me` (self-account-deletion with password; anonymization per ADR 065)
- [x] `POST /auth/accept-invitation`
- [x] Pydantic DTOs for all requests/responses
- [x] DTO convention: `CurrentUser`/`UserSummary` include `initials` and `avatar_color` derived helpers
- [x] Integration tests for happy paths and failure modes
- [x] Test: change-password revokes other sessions
- [x] Test: self-delete preserves authored content (anonymized)
- [x] Cookie attributes verified (`HttpOnly`, `Secure`, `SameSite=Lax`, expiries)

---

### Part C — Backend Domain

#### Phase C1 — Workspace, Members, Invitations, Labels `[ ] Not started`
- [ ] Workspace endpoints (`GET`, `PATCH /workspaces/me`)
- [ ] Member endpoints (list, role change, remove)
- [ ] Member removal anonymizes user + unassigns tasks + deletes sessions
- [ ] Invitation endpoints (list, send, resend) with email queueing
- [ ] Label endpoints (CRUD) with palette validation
- [ ] Label deletion cascades to `task_labels`
- [ ] Integration tests across roles
- [ ] Audit log entries for all mutations

#### Phase C2 — Projects and Project Access `[ ] Not started`
- [ ] Project endpoints (`GET`, `POST`, `GET :id`, `PATCH :id`)
- [ ] Project-access endpoints (`GET`, `POST`, `DELETE`)
- [ ] `assert_project_visible` helper used by `require_project_access`
- [ ] Owner/Admin implicit project visibility
- [ ] Cross-workspace isolation tests
- [ ] Audit log entries

#### Phase C3 — Tasks `[ ] Not started`
- [ ] `GET /projects/:id/tasks` with cursor pagination + filter/sort params
- [ ] `POST /projects/:id/tasks` (defaults: backlog, none priority)
- [ ] `GET /tasks/:id`, `PATCH /tasks/:id`
- [ ] `PATCH /tasks/:id/status` split endpoint
- [ ] Label assignment via PATCH (full set replacement)
- [ ] Last-write-wins semantics (no concurrency token)
- [ ] Workspace-scoping enforced in service layer
- [ ] Audit log entries
- [ ] Integration tests across roles, sort/filter, cancelled-by-default
- [ ] Assignee project-access enforcement
- [ ] FTS column maintenance verified in tests

#### Phase C4 — Comments and @Mentions `[ ] Not started`
- [ ] `GET /tasks/:id/comments` (paginated chronological)
- [ ] `POST /tasks/:id/comments`
- [ ] `PATCH /comments/:id`, `DELETE /comments/:id` (author only) — confirm Open Item #1 first
- [ ] Server-side @mention parser (resolves to workspace members)
- [ ] Comment DTO carries resolved mentions
- [ ] Audit log entry for comment creation
- [ ] Integration tests (post w/ mentions, viewer denied, cross-workspace mentions dropped)

#### Phase C5 — Activity Feed `[ ] Not started`
- [ ] `emit_activity` service helper
- [ ] Wire emission in: task create / status change / assign / unassign / comment create
- [ ] `GET /activity` (workspace + project scope) with cursor pagination
- [ ] Project-access filtering on workspace-scope feed
- [ ] Integration tests (each event type, scope filtering, pagination)
- [ ] Performance smoke test (<50ms at seed scale)

#### Phase C6 — Notifications `[ ] Not started`
- [ ] `dispatch_notifications` service helper (per ADR 070)
- [ ] Wire dispatch for: mention / assignment / status change on assigned / comment on assigned
- [ ] Self-trigger suppression rule
- [ ] `GET /notifications`
- [ ] `POST /notifications/mark-all-read`, `POST /notifications/:id/read`
- [ ] Unread-count query backed by partial index
- [ ] Integration tests for every trigger including self-suppression

#### Phase C7 — Search `[ ] Not started`
- [ ] `GET /search?q=...` with `websearch_to_tsquery`
- [ ] Project-access scoping
- [ ] Result DTO (title, project, status, optional snippet)
- [ ] `ts_rank_cd` ranking; result limit ~20
- [ ] Cancelled tasks excluded by default
- [ ] Integration tests (matching, scope exclusion, malformed query)
- [ ] Performance smoke test (<50ms at seed scale)

#### Phase C8 — Dashboard Endpoints `[ ] Not started`
- [ ] `GET /dashboard/my-tasks` (grouped by project, due-date sorted, overdue first)
- [ ] `GET /dashboard/projects` (with status counts)
- [ ] Integration tests (empty, role-aware, status counts, ordering)
- [ ] Distinct DTOs from ORM models

---

### Part D — Backend Real-Time and Async

#### Phase D1 — Real-Time / WebSocket `[ ] Not started`
- [ ] Add `broadcaster` with Postgres backend
- [ ] `/ws` endpoint with session + CSRF auth
- [ ] Channel subscriptions: `user:{id}`, `workspace:{id}`, `project:{id}` per access
- [ ] Re-subscribe control message on access changes
- [ ] `publish_event` helper (after-commit)
- [ ] Wire publishing into all C-phase service mutations
- [ ] Integration WS tests (mutate via API, assert receipt)
- [ ] Cross-workspace leakage tests
- [ ] 50-connection load smoke

#### Phase D2 — Background Jobs and Email `[ ] Not started`
- [ ] APScheduler jobs (invitation expire, session cleanup, password-reset cleanup, pg_dump)
- [ ] SES adapter (prod) + SMTP-to-MailHog adapter (dev)
- [ ] Email templates (invitation, password reset)
- [ ] `BackgroundTasks` wired for invitation send and password-reset send
- [ ] Manual end-to-end: invitation arrives in MailHog and accept-invitation works

---

### Part E — Backend Hardening

#### Phase E1 — Security: Rate Limiting, Headers, Audit Coverage `[ ] Not started`
- [ ] `slowapi` decorators on login, signup, password-reset request, invitation send
- [ ] 429 response uses ADR 043 envelope with `Retry-After`
- [ ] `infra/nginx/nginx.conf` with security headers per ADR 083
- [ ] nginx routing block (api / ws / web)
- [ ] `nginx -t` runs in CI
- [ ] Audit-coverage walkthrough vs ADR 084 with tests for each event type

#### Phase E2 — Observability `[ ] Not started`
- [ ] Request-ID middleware (UUIDv7 in `X-Request-Id`)
- [ ] Logging middleware (path, method, status, duration_ms, user_id, workspace_id)
- [ ] PII scrubbing processors in structlog
- [ ] Stable auth event names matched by CloudWatch metric filters
- [ ] WebSocket connection gauge emitter
- [ ] PII-leak tests against logs

#### Phase E3 — Backend Test Completion `[ ] Not started`
- [ ] Endpoint coverage audit (every endpoint × role × project access)
- [ ] LISTEN/NOTIFY round-trip integration test
- [ ] FTS integration test
- [ ] Workspace isolation sweep
- [ ] Coverage report: ≥85% on `services/` and `auth/`
- [ ] CI run time ≤10 minutes

#### Phase E4 — Seed Data `[ ] Not started`
- [ ] Idempotent `scripts/seed.py`
- [ ] "Aurora Studio" workspace
- [ ] 5 users covering all roles
- [ ] 3 projects with varied access
- [ ] ~30 tasks across all status/priority/label/due-date combinations
- [ ] Sample comments with @mentions
- [ ] README documents seed credentials

---

### Part F — Frontend Foundation

#### Phase F1 — Frontend Skeleton `[ ] Not started`
- [ ] Vite + React 18 + TS strict
- [ ] Tailwind v3 mapped to CSS custom properties
- [ ] `tokens.css` with every DRD §2 token on `:root`
- [ ] Inter font from Google Fonts
- [ ] TanStack Query v5 with `QueryClientProvider`
- [ ] TanStack Router v1 with empty route tree
- [ ] React Hook Form + Zod added; shared schemas dir
- [ ] `react-intl` + English `locales/en.json`
- [ ] Logical CSS properties enforced
- [ ] Reduced-motion global rule

#### Phase F2 — API Client and Type Codegen `[ ] Not started`
- [ ] `pnpm gen:api` script using `openapi-typescript`
- [ ] `openapi-drift` CI gate
- [ ] Typed `apiClient` with auto CSRF header
- [ ] `useApiQuery` / `useApiMutation` helpers
- [ ] Smoke test against running backend

#### Phase F3 — UI Primitives and Storybook `[ ] Not started`
- [ ] Radix primitives + CVA installed
- [ ] Storybook configured with `vitest-axe`
- [ ] `Button` (Primary/Secondary/Ghost/Destructive)
- [ ] `Input`, `Textarea`, `Select`
- [ ] `Avatar` (deterministic color)
- [ ] `StatusBadge`
- [ ] `LabelChip`
- [ ] `PriorityIcon`
- [ ] `DueDate` (overdue/approaching styling)
- [ ] `Toast` system
- [ ] `Dialog`, `DropdownMenu`, `Tabs`, `Checkbox`, `Tooltip`
- [ ] Lucide icons integrated with default sizing
- [ ] Stories per variant per primitive; axe clean

#### Phase F4 — App Shell `[ ] Not started`
- [ ] `_shell.tsx` three-zone layout (sidebar 240, header 52)
- [ ] Sidebar: logo, primary nav, projects, bottom (Settings + user identity)
- [ ] Header: breadcrumb, search, notification bell, user avatar
- [ ] Logo + wordmark per DRD §5
- [ ] Responsive shell (tablet collapse, mobile hamburger)
- [ ] Route tree per screen inventory §3 (placeholders for all routes)
- [ ] `/projects/:projectId` redirect → `/projects/:projectId/board`
- [ ] Unauthenticated routes (`/login`, `/signup`, `/invitations/:token`) rendered outside the shell
- [ ] `useCurrentUser` hook backed by `/auth/me`

---

### Part G — Frontend Screens

#### Phase G1 — Auth Screens `[ ] Not started`
- [ ] Login screen (DRD §8.1)
- [ ] Signup screen (PRD §3.1)
- [ ] Accept-invitation screen (new + existing user paths, expired state)
- [ ] Password-reset request + confirm screens
- [ ] Form schemas via Zod
- [ ] Mutation hooks hydrate user cache + navigate
- [ ] Component + axe tests

#### Phase G2 — Dashboard `[ ] Not started`
- [ ] Two-column 60/40 grid
- [ ] My Tasks section (groups by project)
- [ ] Recent Activity section (with relative timestamps)
- [ ] Projects section (color dot + status counts)
- [ ] Empty states (role-aware)
- [ ] First-run prompts (Owner / invited user)
- [ ] Create Project modal (reused by sidebar `+`, dashboard empty state, first-run prompt)
- [ ] Wired to dashboard + activity endpoints
- [ ] Component + axe tests

#### Phase G3 — Board View `[ ] Not started`
- [ ] Sub-nav (view toggle, filter button, active filter chips, "Clear all" link, sort dropdown, project settings icon, Create task button)
- [ ] Filter chip bar
- [ ] Five columns; cancelled hidden by default
- [ ] Task cards (title, labels, meta row)
- [ ] Drag-and-drop with `@dnd-kit/core` (desktop only)
- [ ] Optimistic status update with rollback + error toast
- [ ] URL-driven filter + sort state
- [ ] Project Settings modal (Details + Access tabs, screen inventory §5.2)
- [ ] Mobile column stacking, status via dropdown
- [ ] Component + axe tests

#### Phase G4 — List View `[ ] Not started`
- [ ] Sortable columns (title, status, assignee, priority, due, labels)
- [ ] Inline status dropdown (role-gated)
- [ ] Shared filter/sort URL state with board view
- [ ] Mobile responsive (scroll or stacked)
- [ ] Component + axe tests

#### Phase G5 — Task Detail Panel `[ ] Not started`
- [ ] Panel route with backdrop + Esc + × dismissal
- [ ] Slide-in 200ms ease-out, reduced-motion respected
- [ ] Header (title editable, status dropdown, close)
- [ ] Properties (assignee, priority, due date, labels) with inline editors
- [ ] Viewer read-only state
- [ ] Description (rendered Markdown ↔ edit mode)
- [ ] Markdown pipeline (`react-markdown` + `remark-gfm` + `rehype-sanitize`)
- [ ] Comments section (chronological + new comment input)
- [ ] @mention autocomplete
- [ ] Mobile full-screen
- [ ] Component + axe tests

#### Phase G6 — Notifications Page and Badge `[ ] Not started`
- [ ] Notifications page (reverse chronological)
- [ ] Read/unread styling + Mark all as read
- [ ] Click marks read + navigates
- [ ] Header badge bound to unread count
- [ ] Empty state per DRD §16
- [ ] Component + axe tests

#### Phase G7 — Search Overlay `[ ] Not started`
- [ ] Search input + ⌘K trigger
- [ ] Dropdown results (title with match highlight, project, status badge)
- [ ] Keyboard nav (arrows, Enter, Esc)
- [ ] Debounced query against `/search`
- [ ] Empty results message
- [ ] Component + axe tests

#### Phase G8 — Settings (Workspace, Members, Labels, Profile) `[ ] Not started`
- [ ] Settings layout with sub-navigation
- [ ] Workspace tab (name + Save, Owner/Admin only)
- [ ] Members tab (table + invite/remove modals)
- [ ] Labels tab (list + create/edit/delete modals with palette swatches)
- [ ] Profile tab — display name save (`PATCH /auth/me`)
- [ ] Profile tab — change password section (`POST /auth/change-password`)
- [ ] Profile tab — Delete Account modal (`DELETE /auth/me`, password-confirmed)
- [ ] Last-used view per project persisted to `localStorage`
- [ ] Component + axe tests

---

### Part H — Frontend Cross-Cutting

#### Phase H1 — Real-Time Client Bridge `[ ] Not started`
- [ ] WebSocket connection on login with CSRF token
- [ ] `realtimeDispatcher` translating each event type to cache update / invalidate
- [ ] Reconnect with exponential backoff (cap 30s, jittered)
- [ ] Reconnecting indicator
- [ ] `aria-live` announcements
- [ ] Two-context manual test passes (move + see in <1s)

#### Phase H2 — Empty States and First-Run `[ ] Not started`
- [ ] Audit all screens vs DRD §16 table
- [ ] Owner first-run: "Create your first project" prompt on dashboard (uses Create Project modal from G2)
- [ ] Owner first-run: "Invite team members" prompt in sidebar/settings (uses Invite Member modal from G8)
- [ ] Invited-user first-run: brief welcome message on dashboard
- [ ] Visibility derived from workspace state (no backend flag)
- [ ] Role-aware copy & CTAs verified
- [ ] Component tests assert each state

#### Phase H3 — Toasts, Errors, Confirmations `[ ] Not started`
- [ ] Global Zustand toast store + `useToast` hook
- [ ] Toast styling per DRD §7.8 (auto-dismiss, reduced motion)
- [ ] Standardized mutation-error copy
- [ ] Destructive confirmation modal pattern (Remove member, Delete account, Delete label)

#### Phase H4 — Accessibility Pass `[ ] Not started`
- [ ] Keyboard sweep across all routes
- [ ] ARIA on modals, dropdowns, icon buttons, live regions
- [ ] Color contrast spot checks vs tokens
- [ ] Reduced motion verified
- [ ] Manual VoiceOver pass on critical journeys

#### Phase H5 — Frontend Test Completion `[ ] Not started`
- [ ] Component tests for all domain components
- [ ] Hook tests for permission derivations & form schemas
- [ ] `vitest-axe` on every component test
- [ ] Coverage ≥80% on `components/` and `features/`
- [ ] Frontend CI job ≤5 minutes

---

### Part I — E2E, Infrastructure, Deployment

#### Phase I1 — End-to-End Test Suite `[ ] Not started`
- [ ] Playwright config + `@axe-core/playwright`
- [ ] Journey 1: Sign-up → workspace → first project (Owner)
- [ ] Journey 2: Accept invitation (new user)
- [ ] Journey 3: Create task → drag to In Progress → comment with @mention → mark Done
- [ ] Journey 4: Two contexts, real-time move
- [ ] Journey 5: @mention notification real-time badge
- [ ] Journey 6: Search, filter, empty states
- [ ] CI `e2e` job under 15 minutes

#### Phase I2 — Infrastructure (CloudFormation) `[ ] Not started`
- [ ] `network.yml`
- [ ] `compute.yml` (with user-data)
- [ ] `container-registry.yml` (lifecycle policies)
- [ ] `storage.yml` (S3 backups + source maps)
- [ ] `parameters.yml` (SSM SecureString placeholders)
- [ ] `email.yml` (SES + DKIM)
- [ ] `monitoring.yml` (log groups, metric filters, alarms, SNS)
- [ ] `dns.yml` (Route 53, A record, MX/TXT, ACM)
- [ ] `iam.yml` (OIDC + deploy role)
- [ ] `infra/ec2/user-data.sh`
- [ ] `docker-compose.prod.yml` with nginx + api + web + db + certbot
- [ ] Certbot wired (issue + renew)
- [ ] `cfn-lint` clean in CI

#### Phase I3 — CD Pipeline `[ ] Not started`
- [ ] `.github/workflows/deploy.yml`
- [ ] OIDC role assumption
- [ ] Build + push arm64 images to ECR
- [ ] CFN deploy of changed stacks
- [ ] SSM `alembic upgrade head`
- [ ] SSM `docker compose pull && up -d`
- [ ] Health smoke check from workflow
- [ ] Rollback procedure documented in runbook

#### Phase I4 — Production Cutover `[ ] Not started`
- [ ] All SSM Parameter Store values populated
- [ ] First deploy succeeds
- [ ] Let's Encrypt cert issued
- [ ] Route 53 A record cut to Elastic IP
- [ ] Manual smoke (signup → project → task → invite → real-time)
- [ ] SSL Labs grade ≥A
- [ ] Mozilla Observatory grade ≥A

#### Phase I5 — Monitoring and Alarm Verification `[ ] Not started`
- [ ] Operator email subscribed to `taskflow-alerts` SNS
- [ ] Each alarm condition synthesized + verified
- [ ] CloudWatch log groups receiving from all containers
- [ ] Metric filter regexes verified against real log lines
- [ ] Runbook updated

#### Phase I6 — Final Acceptance and Documentation `[ ] Not started`
- [ ] PRD walkthrough against live system
- [ ] DRD page-spec walkthrough
- [ ] All empty states verified
- [ ] `README.md` updated (run, deploy, seed)
- [ ] This status file marked 100% complete
- [ ] Release note authored

---

## Open Items to Confirm Before Their Phase

These were surfaced during plan validation (§6.4 of the implementation plan). Resolve each before its consuming phase begins.

- [ ] **Open Item #1 (before C4):** Comment edit/delete scope — default decision is "author only". Record as ADR or confirm.
- [ ] **Open Item #2 (before G8):** Email change in profile — default is "not exposed in v1". Confirm with PRD revision.
- [ ] **Open Item #3 (before G8):** Last-used view per project storage — default is `localStorage`.
- [ ] **Open Item #4 (before G3):** Project activity feed surface — default is side panel reachable from sub-nav. Confirm with design.
- [ ] **Open Item #5 (before H2):** First-run prompt logic — default derives from workspace state (no backend flag). Confirm.

---

## Notes

Use this section as a running log of decisions, blockers, or context that should persist across sessions.

### 2026-05-02 — Phase 0 complete

- Monorepo scaffolded: `apps/{api,web}`, `packages/{api-types,config}`, `infra/{cloudformation,nginx,ec2}`, `.github/workflows`.
- Biome 1.9.4 (TS/JS) and Ruff 0.7.0 (Python) configured. Biome ignore list excludes `apps/api/`, `infra/`, `docs/`, `episodes/` so it does not lint Python or vendored content.
- Python 3.12 backend uses `pyproject.toml` with hatchling and a placeholder FastAPI app exposing `GET /health` so Phase B1 can grow it without restructuring.
- Both `apps/api/Dockerfile` and `apps/web/Dockerfile` pin `--platform=linux/arm64` per ADR 038. Web Dockerfile is multi-stage (node build → nginx serve).
- `docker-compose.yml` includes db (Postgres 16), MailHog, api, web. `make dev` runs `bootstrap` first to copy `.env.example → .env.local` if absent.
- `docker-compose.prod.yml` is a deliberate placeholder; full topology lands in Phase I2.
- README updated with a "Building TaskFlow Locally" section while preserving the existing methodology content for the YouTube series.

#### Discrepancy review and reconciliation (same day)

A post-Phase-0 audit against the ADRs surfaced 9 issues; all are now fixed:

1. **ADR 082 pre-commit split.** Husky 9.1.6 + lint-staged 15.2.10 run Biome on staged `.ts/.tsx/.js/.jsx/.json`. The `pre-commit` framework runs Ruff on Python and `detect-secrets` on staged content. The Biome hook was removed from `.pre-commit-config.yaml`. The `.husky/pre-commit` script invokes both pipelines.
2. **ADR 086 CodeQL trigger.** Reduced to weekly cron + `workflow_dispatch` only; PR / push triggers removed.
3. **ADR 086 Dependabot scope.** Trimmed to npm + pip only (github-actions and docker ecosystems dropped).
4. **TDD §4 `ruff.toml`.** Removed from the directory tree; replaced with a comment that Ruff config lives in `pyproject.toml [tool.ruff]` per ADR 078. `uv.lock` added to the same line.
5. **TDD §4 `tests/{unit,integration}` subdirs.** Created with empty `__init__.py`.
6. **TDD §4 `alembic.ini`.** Intentionally deferred to Phase B1; not a Phase 0 obligation.
7. **uv dependency management.** `apps/api/pyproject.toml` declares `[tool.uv]`; `apps/api/uv.lock` is committed (49 packages resolved). `Dockerfile` uses the pinned `ghcr.io/astral-sh/uv:0.5.4` image and runs `uv sync --frozen --no-dev`. CI workflow uses `astral-sh/setup-uv@v3` and `uv run …` for Ruff and mypy. `make install` and `make lock` added.
8. **Biome shared base in `packages/config`.** `packages/config/biome.base.json` holds formatter/linter rules; root `biome.json` uses `"extends": ["./packages/config/biome.base.json"]` and keeps only the workspace-specific `vcs` and `files.ignore` blocks. `@taskflow/config` package exports the base config.
9. **`.env.example` completeness.** Added `FRONTEND_BASE_URL`, CORS allowlist, full `slowapi` rate-limit knobs (ADR 052), SES region + from-name (ADR 067), S3 backup + source-maps bucket names (ADR 074), `CERTBOT_EMAIL`, and `PUBLIC_HOSTNAME`.

#### Cross-document edits made for consistency

- `docs/planning/implementation-plan.md` — Phase 0 task list updated: Biome task now reads "root `biome.json` extends `packages/config/biome.base.json`"; Python deps task now says "manage deps with `uv` (lockfile committed at `apps/api/uv.lock`)"; pre-commit task now reads "Husky + lint-staged for Biome on staged TS/JS; `pre-commit` framework for Ruff on Python and `detect-secrets`".
- `docs/technical/technical-design-document.md` — §4 directory tree updated to drop `ruff.toml`, annotate `pyproject.toml` as the home of `[tool.ruff]` and `[tool.mypy]`, and add `uv.lock`.

#### Verification done in this session

- `pnpm install` succeeds (4 workspace projects, 126 packages added). Husky's `prepare` script wires `core.hooksPath = .husky/_`.
- `pnpm exec biome check .` runs clean across 14 files.
- `cd apps/api && uv lock` resolves 49 packages; `uv sync --frozen` installs cleanly.
- `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy taskflow` all green.

#### Runtime verification still TODO

- `make dev` end-to-end boot of the docker-compose stack.
- `pre-commit install` + a synthetic API-key commit to confirm `detect-secrets` blocks.
- A green CI run on a real PR.

### 2026-05-02 — Phase B1 complete

**Files added** (`apps/api/taskflow/`): `main.py`, `settings.py`, `errors.py`, `logging_config.py`, `db/__init__.py`, `db/session.py`, `db/models/__init__.py`, `db/migrations/{env.py,script.py.mako,versions/.gitkeep}`, `api/__init__.py`, `api/v1/__init__.py`. Plus `apps/api/alembic.ini`, `apps/api/tests/conftest.py`, `apps/api/tests/integration/test_skeleton.py`.

**Wire shape:**
- `GET /health` (root) — 200 with `{"status":"ok"}` when `SELECT 1` succeeds, 503 with `{"status":"unhealthy"}` on `SQLAlchemyError`.
- `/api/v1/openapi.json` — FastAPI 0.115 emits OpenAPI 3.1.
- `/api/v1` router mounted, empty (endpoints land in B3+).
- `/api/v1/docs` Swagger UI is exposed in non-prod, suppressed in prod (per ADR 040 / TDD §9.3 "not publicly routed in prod").

**Error envelope (ADR 043 / TDD §9.2):** `{ "error": { "code", "message", "fields"? } }`. `errors.py` defines `AppError` (base, 500) and concrete subclasses `NotFoundError` (404), `PermissionDeniedError` (403), `ConflictError` (409), `RateLimitedError` (429, with `Retry-After`). Three handlers cover `AppError`, `RequestValidationError` (422 with per-field codes), and the catch-all `Exception` (500 opaque envelope, ERROR-level structlog line).

**Logging (ADR 075 / TDD §13.1):** `structlog` with `JSONRenderer` to stdout. `RequestContextMiddleware` is a pure ASGI middleware (not `BaseHTTPMiddleware`, which interacts badly with FastAPI exception handlers — see starlette#1715). Each request binds `request_id`, `path`, `method` into contextvars; emits a `request` log on success / `request.error` on uncaught middleware-side exceptions, including `duration_ms` and `status`. `X-Request-Id` is honored from the inbound header or generated as a `uuid4().hex`, and echoed on the response.

**Settings:** `pydantic-settings` reads `.env.local` (then `.env`); declares `app_env`, `log_level`, `app_base_url`, `frontend_base_url`, `database_url`, `cors_allowed_origins`. Production-only / B3+ keys are not yet declared in `Settings` — they live in `.env.example` and will be added as later phases consume them.

**DB / Alembic:** `db.session` exposes `engine` (asyncpg, `pool_pre_ping=True`), `SessionFactory`, and `get_db()` async generator dependency. `db.models` defines an empty `DeclarativeBase` (`Base`) — concrete tables come in B2. `alembic.ini` keeps `sqlalchemy.url` empty; `migrations/env.py` reads `settings.database_url` and uses `async_engine_from_config` + `connection.run_sync(do_run_migrations)`.

**Tests (`tests/integration/test_skeleton.py`, 10 cases after the reconciliation below):**
- `/health` returns 200 when DB reachable; 503 when SQLAlchemy raises.
- `/api/v1/openapi.json` is a valid 3.1 document and includes `/health`.
- `X-Request-Id` is echoed when sent and generated when absent.
- Per-field validation envelope: wrong type → `INVALID_TYPE`; missing required field → `REQUIRED`.
- App-error envelope on `NotFoundError`, `PermissionDeniedError`, `ConflictError`.
- Unhandled error returns the 500 envelope and emits a single ERROR `request.error` record (with `request_id`, `path`, `method`, `duration_ms`, `exception`) via stdlib log capture.

The DB engine is mocked in `conftest.py` (no Postgres needed for B1). Conftest patches `taskflow.main.{init_engine, get_engine, dispose_engine}` so the lifespan and route share the same fake. The `_test/*` routes are mounted on the live app per-test and torn down after. Tests use `raise_server_exceptions=False` because Starlette's `ServerErrorMiddleware` always re-raises after sending the 500 — a real HTTP client just sees the response, and the test mirrors that.

**Quality gates (run locally):**
- `uv run ruff check .` clean
- `uv run ruff format --check .` clean
- `uv run mypy taskflow tests` — strict, 16 source files, no issues
- `uv run pytest -q` — 10 passed
- `pnpm exec biome check .` clean

**Decisions worth remembering for B2+:**
- Pure ASGI middleware (not `BaseHTTPMiddleware`) is the convention — exception handlers must be the catcher, not user middleware.
- Tests should not define Pydantic models inside fixture function bodies (FastAPI's body-vs-query heuristic gets the wrong namespace). Module-level `BaseModel` subclasses + `Annotated[Model, Body()]` is the safe shape.

#### Discrepancy review and reconciliation (same day)

A post-B1 audit against ADR 043 / 071 / 075 / 082, TDD §7.1 / §9.2 / §9.3 / §13.1, and the implementation-plan tasks surfaced 9 issues. All 9 are now resolved:

1. **ADR 043 canonical validation codes.** `errors.py` now maps Pydantic v2 error `type` strings to canonical SCREAMING_SNAKE codes (`missing → REQUIRED`, `string_type → INVALID_TYPE`, `string_too_short → TOO_SHORT`, `enum → INVALID_CHOICE`, `url_* → INVALID_URL`, `uuid_* → INVALID_UUID`, `datetime_* → INVALID_DATETIME`, `greater_than/less_than/multiple_of → OUT_OF_RANGE`, `value_error → INVALID`, …). Mapping table is committed to `_PYDANTIC_TYPE_TO_CODE` and mirrored in TDD §9.2. New tests assert both `REQUIRED` and `INVALID_TYPE`.
2. **ADR 071 / 082 — pytest in CI.** `ci.yml` gains a `tests` job running `uv run pytest -q` on every PR. Postgres-backed integration tests will land in B2's CI extension.
3. **ADR 075 — stdlib → structlog bridge.** `configure_logging()` now wires `structlog.stdlib.LoggerFactory` and a `ProcessorFormatter` so uvicorn / FastAPI / root-logger lines are rendered as JSON to stdout with the same `ts`/`level`/`exception` shape as structlog events. Fixed-list of bridged loggers: `uvicorn`, `uvicorn.error`, `uvicorn.access`, `fastapi`.
4. **TDD §7.1 engine lifecycle.** `db/session.py` no longer creates the engine at module load. New `init_engine()` / `dispose_engine()` / `get_engine()` functions hold the singleton; lifespan calls them on startup / shutdown. TDD §7.1 step 2 reworded accordingly and step 6 split into "registered at import; lifecycle resources only in lifespan."
5. **TDD §9.3 openapi access policy.** TDD §9.3 amended to clarify that nginx (Phase E1 / ADR 083) is the access boundary; FastAPI exposes `/api/v1/openapi.json` unconditionally and suppresses the Swagger UI at `/api/v1/docs` when `APP_ENV=production`.
6. **Duplicate ERROR logs on unhandled exceptions.** `unhandled_error_handler` no longer logs — the middleware's `request.error` (with full request context + traceback via `format_exc_info`) is the single ERROR record per failed request. TDD §9.2 documents this.
7. **Plan: mypy in CI.** No code change — already satisfied. The `typecheck` job now also includes `tests` so test files are strict-typechecked too.
8. **ADR 042 — `/health` Pydantic model.** `HealthStatus(BaseModel)` defined; `/health` declares `response_model=HealthStatus`. OpenAPI documents the response shape.
9. **CORS middleware.** `CORSMiddleware` wired from `settings.cors_origins_list` with credentials, the relevant methods, `Content-Type` / `X-CSRF-Token` / `X-Request-Id` headers, and `X-Request-Id` exposed.

#### Cross-document edits made for consistency

- `docs/technical/technical-design-document.md`:
  - §7.1 — startup steps reworded; engine is "initialized" in lifespan via `init_engine()`, disposed via `dispose_engine()`. Routes/middleware register at module import; only lifecycle-managed resources go in lifespan.
  - §9.2 — added the canonical Pydantic-type → code mapping table; documented that the middleware is the single ERROR logger for unhandled exceptions.
  - §9.3 — clarified nginx is the gating boundary in production; FastAPI exposes openapi.json unconditionally and suppresses docs UI in prod.
- `docs/planning/implementation-plan.md` — no further edits required.

#### Verification done in this session

- `uv run ruff check .` clean
- `uv run ruff format --check .` clean
- `uv run mypy taskflow tests` — 16 source files, strict, no issues
- `uv run pytest -q` — 10 passed
- `pnpm exec biome check .` clean

### 2026-05-02 — Phase B2 complete

**Files added:**
- `apps/api/taskflow/db/uuid7.py` — wraps `uuid_utils.uuid7()`, returns stdlib `UUID`.
- `apps/api/taskflow/db/models/{__init__,workspace,user,session,invitation,password_reset_token,project,task,label,comment,activity_event,notification,audit_log}.py` — 14 ORM models on a shared `DeclarativeBase` with a naming convention (`pk_*`, `fk_*`, `ix_*`, `uq_*`, `ck_*`).
- `apps/api/taskflow/db/migrations/versions/0001_initial.py` — hand-edited single migration with all tables, hot-path indexes, CHECK constraints, the partial unique index on `users(workspace_id, lower(email)) WHERE deleted_at IS NULL`, and the generated `tasks.search_vector` (`setweight A: title || B: description`) plus its GIN index.
- `apps/api/entrypoint.sh` — runs `alembic upgrade head` then exec's the CMD; wired in `Dockerfile` via `ENTRYPOINT`.
- `apps/api/tests/integration/{conftest.py,test_migration_boot.py}` — Postgres-backed fixtures and migration-boot tests.
- `.github/workflows/ci.yml` — added a `tests` job with a Postgres 16 service container; `TEST_DATABASE_URL` env wires the conftest fixture.

**Schema decisions worth remembering:**
- **`citext` not used.** TDD §8.2 lists `email` as `citext`, but adopting it requires `CREATE EXTENSION citext` and a SQLAlchemy type adapter. We use `text` + a `lower(email)` partial unique index instead — same uniqueness semantics, no extension required. (Worth a TDD note.)
- **`tasks.search_vector`** is a stored `GENERATED ALWAYS AS … STORED` column at the DB level; SQLAlchemy uses `Computed(persisted=True)` so autogenerated migrations would round-trip. Tests assert that inserting a task makes `websearch_to_tsquery('english', :q)` find it.
- **JSONB `metadata` columns** are mapped as `metadata_` Python attribute → `metadata` DB column to avoid colliding with SQLAlchemy's `Base.metadata` attribute.
- **UUIDv7 via `uuid_utils`.** Python 3.13 will get `uuid.uuid7` natively; the wrapper centralizes the dep.

### 2026-05-02 — Phase B3 complete

**Files added (`apps/api/taskflow/auth/`):** `passwords.py`, `tokens.py`, `sessions.py`, `csrf.py`, `permissions.py`, `dependencies.py`, `audit.py`.

- **Argon2id** (`hash_password`, `verify_password`, `needs_rehash`) with parameters `time_cost=3, memory_cost=65536, parallelism=4` per ADR 048. `verify_password` swallows `VerifyMismatchError` and any malformed-hash exceptions — never leaks via stack trace.
- **Session helpers** (`create_session`, `lookup_session`, `delete_session`, `delete_sessions_for_user`, `cleanup_expired_sessions`). Sessions stored in Postgres (ADR 068) with SHA-256-hashed token IDs; CSRF token bytes stored alongside (ADR 051). 7-day idle / 30-day absolute lifetimes per TDD §11.2 / `settings.session_idle_ttl_days` / `settings.session_absolute_ttl_days`.
- **CSRF double-submit** (`csrf.csrf_check`) — GET/HEAD/OPTIONS pass, mutating methods require cookie + header to match each other AND the session's bound CSRF token. `hmac.compare_digest` for constant-time compare.
- **Permission table** (`auth.permissions`) — `Action` enum + `PERMISSIONS` table that mirrors PRD §2.1 exactly. `is_allowed(role, action)` and `has_implicit_project_access(role)`. Unit-tested cell-by-cell against the PRD.
- **FastAPI dependencies** in `auth/dependencies.py`: `get_db`, `current_session` (refreshes `last_seen_at`, raises 401 `UNAUTHENTICATED` on missing/expired/idle), `current_user` (rejects `deleted_at IS NOT NULL` per ADR 065), `current_workspace`, `require_action(Action)` factory, `require_project_access(project_id_param)` factory, `verify_csrf` middleware-style dep.
- **Audit helper** (`auth/audit.write_audit_log`) — synchronous, in-transaction; pulls IP + UA off `Request`. Caller commits.

**Tests added (`apps/api/tests/unit/`):** `test_passwords.py`, `test_csrf.py`, `test_permissions.py`, `test_tokens.py`. All four DB-free; 20 assertions total covering happy paths, mismatches, malformed hashes, and the entire role × action grid.

### 2026-05-02 — Phase B4 complete

**Files added:** `apps/api/taskflow/schemas/{users,auth}.py`, `apps/api/taskflow/services/auth.py`, `apps/api/taskflow/api/v1/auth.py`. The v1 router now mounts the `/auth` sub-router.

**DTOs (screen inventory §8 / TDD §11):**
- `UserSummary` and `CurrentUser` carry `initials` (derived from `display_name` with email-first-char fallback) and `avatar_color` (one of six DRD §2.10 colors keyed by SHA-256 of the user UUID — deterministic and stable).
- `SignupRequest`, `LoginRequest`, `PasswordResetRequest`/`PasswordResetConfirm`, `ChangePasswordRequest`, `UpdateProfileRequest`, `DeleteAccountRequest`, `AcceptInvitationRequest`/`AcceptInvitationResponse`, `OkResponse`. Email validated via `EmailStr` (`pydantic[email]`); password rules: 8–128 chars (canonical floor; tightened later if PRD specifies).

**Endpoints (10):**
- `POST /api/v1/auth/signup` — atomic workspace + Owner + initial session; backfills `workspaces.created_by` after the user row exists. Audit `auth.signup`.
- `POST /api/v1/auth/login` — verifies password, creates session, sets `taskflow_session` (HttpOnly) + `csrf_token` (JS-readable) cookies. Audit `auth.login.success` / `auth.login.failure`.
- `POST /api/v1/auth/logout` — verify_csrf-gated; deletes session row, clears cookies. Audit `auth.logout`.
- `POST /api/v1/auth/password-reset/request` — no-enumeration: always returns 200; if the user exists, generates a 1-hour single-use token (ADR 049) and dispatches an email via `BackgroundTasks` (the dispatch function is a stub today; D2 wires SES/MailHog).
- `POST /api/v1/auth/password-reset/confirm` — verifies token (hash, expiry, unused), updates password, revokes ALL sessions for the user. Audit `auth.password_reset.completed`.
- `GET /api/v1/auth/me` — returns `CurrentUser`.
- `PATCH /api/v1/auth/me` — display-name only (PRD §20.1); audit `auth.profile.updated`.
- `POST /api/v1/auth/change-password` — verifies current, rehashes, revokes OTHER sessions (current survives). Audit `auth.password.changed`.
- `DELETE /api/v1/auth/me` — body `{password}` confirms identity; in-place anonymization per ADR 065 / TDD §11.7 (clears `email`/`name`/`password_hash`, sets `deleted_at`, deletes sessions, `UPDATE tasks SET assignee_id = NULL`). Audit `auth.account_deleted`.
- `POST /api/v1/auth/accept-invitation` — token + optional `password`/`display_name`. Existing-user path moves them to the new workspace + role; new-user path requires both fields. Audit `workspace.invitation.accepted`.

**Tests added:** `tests/integration/test_auth_endpoints.py` — 18 cases covering happy paths, duplicate-email, invalid password 422, wrong-password 401, /me 401-when-unauthenticated, CSRF gating on logout, no-enumeration on password reset, session revocation on confirm, change-password's other-session revocation, self-delete anonymization, invitation expiry/invalid/new-user. Plus a UUIDv7 ordering check.

**Tests strategy:**
- DB-backed tests use the `db_session` / `db_engine` fixtures from `tests/integration/conftest.py`. They `pytest.skip(...)` cleanly if Postgres isn't reachable at `TEST_DATABASE_URL` (default `postgresql+asyncpg://taskflow:taskflow@localhost:5432/taskflow_test`). On CI the new `tests` job runs a `postgres:16-alpine` service; locally the user runs `make dev` (or starts Docker + `docker compose up -d db`) before `pytest`.
- The TestClient runs against an `httpx.AsyncClient` + `ASGITransport` so async DB sessions and async route handlers share an event loop without `BaseHTTPMiddleware`-style quirks.
- `cookie_secure = False` is set in the `app` fixture so the (HTTP) `TestClient` keeps cookies across requests; production stays `True`.

**Quality gates (run locally):**
- `uv run ruff check .` clean
- `uv run ruff format --check .` clean
- `uv run mypy taskflow tests` — strict, 50 source files, no issues
- `uv run pytest -q` — 31 passed, 21 skipped (the 21 are the DB-backed integration tests; CI Postgres service runs them)
- `pnpm exec biome check .` clean

### Runtime verification still TODO (cumulative for Part B)

- `make dev` end-to-end boot of the full docker-compose stack (db + mailhog + api + web). **Done 2026-05-09 — see closeout note below.**
- `make test` → all integration tests green against a real Postgres (locally requires Docker). **Done 2026-05-09 — 57 passed, 0 skipped.**
- A green CI run on a real PR (the new `tests` job will exercise B2's migration-boot test and the B4 endpoint tests). **Partial — `tests` and `lint` jobs proven green on all 5 Dependabot PRs from 2026-05-02 (only `typecheck` failed because the bumped dep itself was incompatible). A fully-green PR is still pending.**

### 2026-05-02 — Part B reconciliation

A post-Part-B audit against ADRs 047–051, 062–065, 075, 084, TDD §8.2 / §11, PRD §2.1 / §3.3, and the implementation-plan tasks surfaced 16 items. All 16 are now resolved (or accepted with documentation):

1. **ADR 049 — prior tokens not invalidated.** `services/auth.request_password_reset` now `UPDATE password_reset_tokens SET used_at = now() WHERE user_id = ? AND used_at IS NULL` before inserting the new row. Only the most recent token is valid.
2. **ADR 084 — audit event names aligned.** `auth.password.changed → auth.password_changed`; `auth.account_deleted → account.deleted`. `AUDIT_EVENT_TYPES` tuple in `db/models/audit_log.py` now matches ADR 084 exactly. ADR 084 was amended to add `auth.signup` and `auth.profile.updated` (extensions used by B4) plus `workspace.invitation.resent` (used by C1) and a naming-convention note.
3. **Plan / TDD §11.5 — `require_role(*roles)`.** Added in `auth/dependencies.py` alongside `require_action(Action)`. `require_action` remains the recommended primitive (PRD §2.1-driven); `require_role` is the spec-named role-floor variant.
4. **TDD §8.2 — `citext` for email columns.** `users.email` and `invitations.email` now use `postgresql.CITEXT()`. Migration adds `CREATE EXTENSION IF NOT EXISTS citext` and the partial unique index drops the `lower(email)` wrapper since citext is case-insensitive natively.
5. **TDD §8.2 — `csrf_token` is 32 raw bytes.** `auth/sessions.create_session` generates `secrets.token_bytes(32)` and stores the raw bytes in `sessions.csrf_token`. New helpers `encode_csrf` / `decode_csrf` URL-safe-base64 the bytes for cookie + `X-CSRF-Token` transport. `csrf_check` decodes the header and compares constant-time against the stored bytes.
6. **ADR 065 — history-bearing FKs no longer cascade.** Dropped `ondelete="SET NULL"` from `comments.author_id`, `tasks.created_by`, `activity_events.actor_id`, `audit_log.actor_id`, `notifications.actor_id`, `projects.created_by`, `workspaces.created_by`. Only `tasks.assignee_id` keeps `SET NULL` per ADR 065's explicit "becomes unassigned" rule.
7. **Plan typo `confirmed` → `completed`.** Fixed in `docs/planning/implementation-plan.md` to match ADR 084.
8. **CHECK on `audit_log.event_type`.** Added in both ORM (`audit_log.py`) and migration (`0001_initial.py`) using `AUDIT_EVENT_TYPES` as the source of truth.
9. **ADR 084 — added `auth.signup`, `auth.profile.updated`, `workspace.invitation.resent`** to the canonical event table, with a naming-convention paragraph explaining the dot-vs-underscore mix.
10. **Direct `lookup_session` rejection tests** added to `tests/integration/test_lookup_session.py`: unknown token, absolute-expiry, idle-expiry, and last-seen-refresh on success.
11. **Cookie `Max-Age=2592000` assertion** added to the signup test (30-day absolute lifetime per TDD §11.1). Also asserts CSRF cookie is *not* HttpOnly (per ADR 051).
12. **Login rate-limit TODO comments** on `signup`, `login`, and `password-reset/request` endpoints citing ADR 052 limits and Phase E1.
13. **PRD §3.3** clarified: accepting an invitation as an existing user **replaces** their workspace membership (consequence of the one-workspace-per-user rule in §4.1).
14. **CHECK on `labels.color`.** Hardcoded the 8-color DRD §2.9 palette as a CHECK constraint in both ORM and migration. Project color stays open (no fixed enumeration in DRD).
15. **`requires_db` pytest marker** with auto-marking in `tests/integration/conftest.py` — any test using `db_engine` / `db_session` is now automatically marked `requires_db` and the session fixture skips the entire chain when Postgres is unreachable.
16. **Runtime e2e** still pending (Docker not started in this session). CI will exercise it on the next push.

#### Cross-document edits

- `docs/technical/decisions/084-audit-logging-scope.md` — three new event types, naming-convention note, CHECK-constraint reference.
- `docs/product/product-requirements-document.md` (§3.3) — workspace-replacement note for invitation acceptance.
- `docs/planning/implementation-plan.md` — typo fix on the password-reset audit event.
- `docs/planning/implementation-status.md` — this section.

#### Verification done in this session

- `pnpm exec biome check .` — clean (14 files)
- `uv run ruff check .` / `ruff format --check .` — clean
- `uv run mypy taskflow tests` — strict, **51 source files**, no issues
- `uv run pytest -q` — **32 passed, 25 skipped** (skipped = `requires_db` tests; CI Postgres service runs them)
- `alembic upgrade head --sql` (offline) — renders cleanly, includes `CREATE EXTENSION citext`, `email CITEXT`, label-palette CHECK, audit_log event-type CHECK, and history-FKs without `ON DELETE`

### 2026-05-09 — Part B runtime verification closeout

The three TODOs from the cumulative Part B verification block were exercised end-to-end in Docker. Two real bugs surfaced and were fixed in this session.

**`make dev` boot.** All four services healthy: `db` (Postgres 16, healthcheck passing), `mailhog` (UI at :8025), `api` (`GET /health` → 200 with `X-Request-Id`; `/api/v1/openapi.json` is OpenAPI 3.1 listing the 8 B4 auth paths; structlog JSON output to stdout; `alembic upgrade head` ran on entrypoint, applying `0001_initial`), `web` (Vite dev server at :5173).

**`make test` against real Postgres.** `docker compose -f docker-compose.test.yml run --rm api-test` → **57 passed, 0 skipped** in 2.7s. Every `requires_db` test (B2 migration boot, B3 session lookup, B4 endpoint integration) ran green.

**`detect-secrets` blocks a fake key.** `pre-commit run detect-secrets` against a synthetic file containing an AWS key pair — flagged as AWS Access Key + Base64 + Secret Keyword, exit 1. Husky's `.husky/pre-commit` script invokes `pre-commit run --hook-stage pre-commit`, so the same dispatch fires on a real `git commit`.

**Green CI on a real PR.** Partial. All 5 open Dependabot PRs from 2026-05-02 had `tests` and `lint` jobs green; only `typecheck` failed, and only because the bumped dependency itself doesn't typecheck (e.g., vite 5→8 is a breaking major). The workflow infrastructure is healthy. A fully-green PR is the natural next milestone, separate from this verification.

#### Bugs found and fixed

1. **`docker-compose.yml` — web service** failed to boot with `vite: Resource deadlock would occur`. The host's macOS-built `node_modules` were bind-mounted via `- .:/app` into the Linux container, where Vite's binary couldn't be flock'd. Fixed by adding anonymous volumes for `/app/node_modules` and `/app/apps/web/node_modules`, which mask the host's directories so the container's `pnpm install` populates a clean Linux tree.
2. **`docker-compose.test.yml` — api-test service** could not actually run the test suite. Two issues:
   - The conftest reads `TEST_DATABASE_URL`, but the test compose only set `DATABASE_URL`. Without the env var the conftest fell back to `localhost:5432/taskflow_test`, hit `OperationalError`, and silently `pytest.skip`'d every `requires_db` test. Fixed by adding `TEST_DATABASE_URL` matching the in-network `db:5432/taskflow_test`.
   - The image is built `uv sync --frozen --no-dev`, so pytest is not on the PATH. Fixed by changing the command to `sh -c "uv sync --frozen && exec pytest -q"` — this installs the dev group at container start (the image already has `pyproject.toml` + `uv.lock` baked in, so no external network dependency).
