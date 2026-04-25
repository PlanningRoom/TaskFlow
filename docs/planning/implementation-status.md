# TaskFlow — Implementation Status

**Last Updated:** 2026-04-25
**Current Phase:** Not started
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
| A | Foundation | 1 | 0 | 0 | 0 |
| B | Backend Core | 4 | 0 | 0 | 0 |
| C | Backend Domain | 8 | 0 | 0 | 0 |
| D | Backend Real-Time & Async | 2 | 0 | 0 | 0 |
| E | Backend Hardening | 4 | 0 | 0 | 0 |
| F | Frontend Foundation | 4 | 0 | 0 | 0 |
| G | Frontend Screens | 8 | 0 | 0 | 0 |
| H | Frontend Cross-Cutting | 5 | 0 | 0 | 0 |
| I | E2E, Infra, Deploy | 6 | 0 | 0 | 0 |
| **Total** | | **42** | **0** | **0** | **0** |

---

## Phase Status

### Part A — Foundation

#### Phase 0 — Project Foundation `[ ] Not started`
- [ ] Initialize pnpm workspaces monorepo with Turborepo
- [ ] Create directory layout (apps, packages, infra, .github)
- [ ] Add `pnpm-workspace.yaml`, `turbo.json`, root `package.json`, `Makefile`
- [ ] Configure Biome (TS/JS) and Ruff (Python)
- [ ] Set up Python 3.12+ with `pyproject.toml`
- [ ] Author `docker-compose.yml` (dev), `.test.yml`, `.prod.yml` placeholder
- [ ] Author `apps/web/Dockerfile` and `apps/api/Dockerfile` (arm64 stubs)
- [ ] Add MailHog to dev compose
- [ ] Author `.env.example`
- [ ] GitHub Actions `ci.yml` with `lint` and `typecheck` jobs
- [ ] Configure Dependabot and CodeQL
- [ ] Configure pre-commit hooks
- [ ] Root `README.md` with quickstart

---

### Part B — Backend Core

#### Phase B1 — Backend Skeleton `[ ] Not started`
- [ ] Add FastAPI + Uvicorn to `apps/api`; main.py entry point
- [ ] Implement `settings.py` via `pydantic-settings`
- [ ] Implement async SQLAlchemy session in `db/session.py`
- [ ] Configure Alembic with `alembic.ini` and `env.py`
- [ ] Implement global error contract in `errors.py` (per ADR 043)
- [ ] Configure structured logging with `structlog` + request-id middleware
- [ ] Implement `GET /health` (200 if Postgres reachable)
- [ ] Wire `/api/v1` prefix and empty router
- [ ] Expose `/api/v1/openapi.json`
- [ ] Add `mypy` to CI typecheck job

#### Phase B2 — Database Schema and Migrations `[ ] Not started`
- [ ] SQLAlchemy ORM models for all 14 tables (TDD §8.2)
- [ ] UUIDv7 primary keys, `created_at`/`updated_at` columns
- [ ] Partial unique index on `users(workspace_id, lower(email)) WHERE deleted_at IS NULL`
- [ ] `tasks.search_vector` generated column + GIN index
- [ ] All hot-path indexes (TDD §17.1)
- [ ] CHECK constraints for enum-like text columns
- [ ] Initial Alembic migration `0001_initial.py`
- [ ] Migration boot test (empty → head → assert schema)
- [ ] Migrations run on container startup

#### Phase B3 — Authentication and Authorization Core `[ ] Not started`
- [ ] Argon2id password hashing (`hash_password`, `verify_password`)
- [ ] Session creation/lookup/cleanup helpers
- [ ] CSRF double-submit helpers
- [ ] FastAPI dependencies: `get_db`, `current_session`, `current_user`, `current_workspace`, `require_role`, `require_project_access`, `verify_csrf`
- [ ] Permission table in `auth/permissions.py`
- [ ] `audit_log` write helper (synchronous, in-transaction)
- [ ] Unit tests for permission table (every role × action × project-access cell)
- [ ] Unit tests for password hashing
- [ ] Unit tests for CSRF (mismatch, missing, GET bypass)

#### Phase B4 — Authentication Endpoints `[ ] Not started`
- [ ] `POST /auth/signup` (creates workspace + Owner)
- [ ] `POST /auth/login` (sets cookies, audit log)
- [ ] `POST /auth/logout`
- [ ] `POST /auth/password-reset/request` (no enumeration)
- [ ] `POST /auth/password-reset/confirm` (revokes sessions)
- [ ] `GET /auth/me`
- [ ] `PATCH /auth/me` (display name only; email read-only per PRD §20.1)
- [ ] `POST /auth/change-password` (verify current, hash new, revoke other sessions)
- [ ] `DELETE /auth/me` (self-account-deletion with password; anonymization per ADR 065)
- [ ] `POST /auth/accept-invitation`
- [ ] Pydantic DTOs for all requests/responses
- [ ] DTO convention: `CurrentUser`/`UserSummary` include `initials` and `avatar_color` derived helpers
- [ ] Integration tests for happy paths and failure modes
- [ ] Test: change-password revokes other sessions
- [ ] Test: self-delete preserves authored content (anonymized)
- [ ] Cookie attributes verified (`HttpOnly`, `Secure`, `SameSite=Lax`, expiries)

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

_(empty)_
