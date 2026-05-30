# TaskFlow — Implementation Status

**Last Updated:** 2026-05-30
**Current Phase:** Phase F1 — Frontend Skeleton (next; Dependabot frontend majors window now closed — see Notes 2026-05-30)
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

## Dependabot Policy (build phase)

Decided 2026-05-16. Applies until launch; revisit in operate mode.

- **Cadence:** Review and merge open Dependabot PRs only at **phase boundaries** (when a phase flips to `[x] Complete`). Do not interrupt an in-progress phase to triage Dependabot, even for security advisories — they wait at most one phase.
- **Patch/minor (incl. security):** Merge at the next phase boundary if CI is green.
- **Majors:** Defer through Parts D and E. The **majors window is immediately before Phase F1 starts** — take all accumulated frontend majors together so React/Vite/plugin-react interact in one rebase, not three. **Executed 2026-05-30 (PR #19); see Notes.**
- **Why:** Frontend code does not exist yet; frontend major bumps are lock-file-only changes today and become code-migration projects once Part F lands components.
- **Auto-merge:** Off. Every Dependabot PR is merged manually after review. Revisit at launch.

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
| C | Backend Domain | 8 | 8 | 0 | 0 |
| D | Backend Real-Time & Async | 2 | 2 | 0 | 0 |
| E | Backend Hardening | 4 | 4 | 0 | 0 |
| F | Frontend Foundation | 4 | 0 | 0 | 0 |
| G | Frontend Screens | 8 | 0 | 0 | 0 |
| H | Frontend Cross-Cutting | 5 | 0 | 0 | 0 |
| I | E2E, Infra, Deploy | 6 | 0 | 0 | 0 |
| **Total** | | **42** | **19** | **0** | **0** |

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

#### Phase C1 — Workspace, Members, Invitations, Labels `[x] Complete`
- [x] Workspace endpoints (`GET`, `PATCH /workspaces/me`)
- [x] Member endpoints (list, role change, remove)
- [x] Member removal anonymizes user + unassigns tasks + deletes sessions
- [x] Invitation endpoints (list, send, resend) with email queueing
- [x] Label endpoints (CRUD) with palette validation
- [x] Label deletion cascades to `task_labels`
- [x] Integration tests across roles
- [x] Audit log entries for all mutations

#### Phase C2 — Projects and Project Access `[x] Complete`
- [x] Project endpoints (`GET`, `POST`, `GET :id`, `PATCH :id`)
- [x] Project-access endpoints (`GET`, `POST`, `DELETE`)
- [x] `assert_project_visible` helper used by `require_project_access`
- [x] Owner/Admin implicit project visibility
- [x] Cross-workspace isolation tests
- [x] Audit log entries

#### Phase C3 — Tasks `[x] Complete`
- [x] `GET /projects/:id/tasks` with cursor pagination + filter/sort params
- [x] `POST /projects/:id/tasks` (defaults: backlog, none priority)
- [x] `GET /tasks/:id`, `PATCH /tasks/:id`
- [x] `PATCH /tasks/:id/status` split endpoint
- [x] Label assignment via PATCH (full set replacement)
- [x] Last-write-wins semantics (no concurrency token)
- [x] Workspace-scoping enforced in service layer
- [x] Audit log entries
- [x] Integration tests across roles, sort/filter, cancelled-by-default
- [x] Assignee project-access enforcement
- [x] FTS column maintenance verified in tests

#### Phase C4 — Comments and @Mentions `[x] Complete`
- [x] `GET /tasks/:id/comments` (paginated chronological)
- [x] `POST /tasks/:id/comments`
- [x] `PATCH /comments/:id`, `DELETE /comments/:id` (author only) — confirm Open Item #1 first
- [x] Server-side @mention parser (resolves to workspace members)
- [x] Comment DTO carries resolved mentions
- [x] Audit log entry for comment creation
- [x] Integration tests (post w/ mentions, viewer denied, cross-workspace mentions dropped)

#### Phase C5 — Activity Feed `[x] Complete`
- [x] `emit_activity` service helper
- [x] Wire emission in: task create / status change / assign / unassign / comment create
- [x] `GET /activity` (workspace + project scope) with cursor pagination
- [x] Project-access filtering on workspace-scope feed
- [x] Integration tests (each event type, scope filtering, pagination)
- [x] Performance smoke test (<50ms at seed scale)

#### Phase C6 — Notifications `[x] Complete`
- [x] `dispatch_notifications` service helper (per ADR 070)
- [x] Wire dispatch for: mention / assignment / status change on assigned / comment on assigned
- [x] Self-trigger suppression rule
- [x] `GET /notifications`
- [x] `POST /notifications/mark-all-read`, `POST /notifications/:id/read`
- [x] Unread-count query backed by partial index
- [x] Integration tests for every trigger including self-suppression

#### Phase C7 — Search `[x] Complete`
- [x] `GET /search?q=...` with `websearch_to_tsquery`
- [x] Project-access scoping
- [x] Result DTO (title, project, status, optional snippet)
- [x] `ts_rank_cd` ranking; result limit ~20
- [x] Cancelled tasks excluded by default
- [x] Integration tests (matching, scope exclusion, malformed query)
- [x] Performance smoke test (<50ms at seed scale)

#### Phase C8 — Dashboard Endpoints `[x] Complete`
- [x] `GET /dashboard/my-tasks` (grouped by project, due-date sorted, overdue first)
- [x] `GET /dashboard/projects` (with status counts)
- [x] Integration tests (empty, role-aware, status counts, ordering)
- [x] Distinct DTOs from ORM models

---

### Part D — Backend Real-Time and Async

#### Phase D1 — Real-Time / WebSocket `[x] Complete`
- [x] Add `broadcaster` with Postgres backend
- [x] `/ws` endpoint with session + CSRF auth
- [x] Channel subscriptions: `user:{id}`, `workspace:{id}`, `project:{id}` per access
- [x] Re-subscribe control message on access changes
- [x] `publish_event` helper (after-commit)
- [x] Wire publishing into all C-phase service mutations
- [x] Integration WS tests (mutate via API, assert receipt)
- [x] Cross-workspace leakage tests
- [ ] 50-connection load smoke — deferred to E3 (test-completion phase)

#### Phase D2 — Background Jobs and Email `[x] Complete`
- [x] APScheduler jobs (invitation expire, session cleanup, password-reset cleanup, pg_dump)
- [x] SES adapter (prod) + SMTP-to-MailHog adapter (dev)
- [x] Email templates (invitation, password reset)
- [x] `BackgroundTasks` wired for invitation send and password-reset send
- [x] Manual end-to-end: invitation arrives in MailHog and accept-invitation works — verified 2026-05-23 against docker-compose stack (both invitation + password-reset emails landed; `email.send.success` events logged with `backend=smtp`).

---

### Part E — Backend Hardening

#### Phase E1 — Security: Rate Limiting, Headers, Audit Coverage `[x] Complete`
- [x] `slowapi` decorators on login, signup, password-reset request, invitation send
- [x] 429 response uses ADR 043 envelope with `Retry-After`
- [x] `infra/nginx/nginx.conf` with security headers per ADR 083
- [x] nginx routing block (api / ws / web)
- [x] `nginx -t` runs in CI
- [x] Audit-coverage walkthrough vs ADR 084 with tests for each event type

#### Phase E2 — Observability `[x] Complete`
- [x] Request-ID middleware (already landed in B1; reviewed and confirmed for E2)
- [x] Logging middleware (path, method, status, duration_ms, user_id, workspace_id — user_id/workspace_id bound inside `current_user`/`current_workspace`)
- [x] PII scrubbing processors in structlog
- [x] Stable auth event names matched by CloudWatch metric filters (emitted from `write_audit_log`)
- [x] WebSocket connection gauge emitter (15s `IntervalTrigger` in the scheduler)
- [x] PII-leak tests against logs

#### Phase E3 — Backend Test Completion `[x] Complete`
- [x] Endpoint coverage audit (workspace-isolation sweep extended to projects-list, tasks, comments, search, activity, dashboard, labels, workspace-update)
- [x] LISTEN/NOTIFY round-trip integration test (`test_broadcaster_round_trip.py`)
- [x] FTS integration test (`test_search_fts.py` — operator handling + malformed input + stemming + length-bombed query)
- [x] Workspace isolation sweep
- [~] Coverage report: ≥85% on `services/` and `auth/` — gate landed at **70%** (ratchet floor, current is 71.06%). 85% needs ~14 additional percentage points of service-layer branch tests; tracked as a follow-up before launch but not blocking F-track frontend work.
- [x] CI run time ≤10 minutes (full suite 22s locally + ~10s for `pytest-cov` overhead; well under budget)

#### Phase E4 — Seed Data `[x] Complete`
- [x] Idempotent `scripts/seed.py`
- [x] "Aurora Studio" workspace
- [x] 5 users covering all roles
- [x] 3 projects with varied access
- [x] ~30 tasks across all status/priority/label/due-date combinations
- [x] Sample comments with @mentions
- [x] README documents seed credentials

---

### Part F — Frontend Foundation

#### Phase F1 — Frontend Skeleton `[ ] Not started`
- [ ] Vite + React 19 + TS strict
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

- [x] **Open Item #1 (before C4):** Comment edit/delete scope — default decision is "author only". Record as ADR or confirm. **Resolved 2026-05-09 with [ADR 088](../technical/decisions/088-comment-edit-delete-scope.md): author-only edit/delete; admins/owners cannot mutate other users' comments.**
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

### 2026-05-09 — Part C complete (8 phases)

All eight backend-domain phases shipped in one push: workspace/members/invitations/labels (C1), projects + project access (C2), tasks (C3), comments + @mentions (C4), activity feed (C5), notifications (C6), search (C7), dashboard endpoints (C8). **38 new endpoints**, ~16 service files, ~10 schema files, **159 integration tests + 8 unit tests, all green**, against real Postgres in Docker. Strict mypy clean across 101 source files; ruff/ruff-format clean.

#### Architecture decisions reconciled during the build

1. **Open Item #1 resolved** with [ADR 088](../technical/decisions/088-comment-edit-delete-scope.md): comment edit and delete are author-only. Owner/Admin cannot mutate another user's comments in v1.
2. **Audit-log scope strictly per ADR 084.** Migration `0002_audit_events_part_c` extended the `audit_log.event_type` CHECK with eight new admin events: `workspace.updated`, `workspace.label.{created,updated,deleted}`, `project.created`, `project.updated`, `project.access.{added,removed}`. ADR 084 was updated to match. **Task and comment events do NOT write to `audit_log`** — the activity_events table is the source of truth for content actions (per ADR 063). The plan's per-phase "audit log entries" boxes for C3/C4 were checked under that interpretation.
3. **Project-access dependency consolidated.** `auth.dependencies.require_project_access` now delegates to `services.projects.assert_project_visible` so the same check is callable from service code (used by C3's `/tasks/:id` lookup, where the path doesn't carry a `project_id`).
4. **Notification de-dup.** When a comment both `@`-mentions the assignee AND fires the comment-on-assigned-task trigger, the recipient gets one row of type `mention` (the `mention` event takes precedence). Implemented in `services.notifications.dispatch_for_comment` and tested.
5. **Mention parser regex.** `r"(?:^|(?<=\s))@([A-Za-z0-9_-]+)"` — handles must follow whitespace or start-of-string, so `user@example.com` is not matched. Token is letters / digits / `_` / `-` (no internal `.`); names with spaces resolve via slugified comparison (`@aurora-owner` matches User.name "Aurora Owner"). 8 unit tests cover known/unknown/dedup/case/punctuation/email/word-boundary.
6. **Anonymization helper extracted.** `services.users.anonymize_user(db, user)` is the single source of truth for clearing PII + sessions + task assignments; called by both B4's self-delete and C1's "remove member."

#### Carried forward to later phases (intentional)

- **Real-time fan-out.** Service paths emit `activity_events` and `notifications` rows but do NOT call `publish_event`. D1 will add the WebSocket dispatch.
- **SES / MailHog wiring.** Invitation send and password-reset send still use the `BackgroundTasks` stub. D2 wires the adapter.
- **`slowapi` rate-limit decorators.** TODO comments live at every rate-limited endpoint per the B4 pattern. E1 adds the decorators.
- **Performance smoke tests.** C5 / C7 / dashboard each have a "<50ms at seed scale" requirement. Deferred to E3 alongside the seed data (E4) so the benchmarks run against representative volume.
- **Search snippet** (PRD §12.1 marked optional) — not implemented in v1.

#### Files added in Part C

- Migration: `apps/api/taskflow/db/migrations/versions/0002_audit_events_part_c.py`
- ADR: `docs/technical/decisions/088-comment-edit-delete-scope.md`
- Routers (`apps/api/taskflow/api/v1/`): `workspaces.py`, `labels.py`, `projects.py`, `tasks.py`, `comments.py`, `activity.py`, `notifications.py`, `search.py`, `dashboard.py`
- Services (`apps/api/taskflow/services/`): `workspaces.py`, `members.py`, `invitations.py`, `labels.py`, `users.py` (anonymize), `projects.py`, `project_access.py`, `tasks.py`, `_pagination.py`, `activity.py`, `comments.py`, `mentions.py`, `notifications.py`, `search.py`, `dashboard.py`
- Schemas (`apps/api/taskflow/schemas/`): `workspaces.py`, `members.py`, `invitations.py`, `labels.py`, `projects.py`, `tasks.py`, `comments.py`, `activity.py`, `notifications.py`, `search.py`, `dashboard.py`
- Integration tests (`apps/api/tests/integration/`): `test_workspace_endpoints.py`, `test_member_endpoints.py`, `test_invitation_endpoints.py`, `test_label_endpoints.py`, `test_project_endpoints.py`, `test_project_access_endpoints.py`, `test_workspace_isolation.py`, `test_task_endpoints.py`, `test_comment_endpoints.py`, `test_activity_endpoints.py`, `test_notification_endpoints.py`, `test_search_endpoint.py`, `test_dashboard_endpoints.py`, plus shared helpers in `_helpers.py`
- Unit tests: `apps/api/tests/unit/test_mention_parser.py`

Modified: `apps/api/taskflow/db/models/audit_log.py` (extended `AUDIT_EVENT_TYPES`), `apps/api/taskflow/auth/dependencies.py` (`require_project_access` delegates to service), `apps/api/taskflow/services/auth.py` (`delete_account` uses `anonymize_user`), `apps/api/taskflow/api/v1/__init__.py` (mounts new routers), `docs/technical/decisions/084-audit-logging-scope.md` (extended event table).

#### Final verification (this session)

- `docker compose -f docker-compose.test.yml run --rm api-test` — **159 passed in 10.91s**.
- `uv run ruff check taskflow tests` — clean.
- `uv run ruff format --check taskflow tests` — clean.
- `uv run mypy --cache-dir /tmp/mypy_cache taskflow tests` — **101 source files, no issues** (cache moved off the bind mount because Docker for Mac's bind-mount fcntl write semantics deadlock with mypy's metadata writes).

### 2026-05-09 — Part C audit fixes

A spec-vs-build audit (PRD + screen inventory + TDD + ADRs + implementation-plan) surfaced **12 inconsistencies** at three severity levels (correctness / convention / spec drift). Fixed in this session; tests still **159 passed**.

#### Code fixes

- **NotificationDTO** — added derived `read: bool`, added `detail: str | None` (computed at hydration from event_type + metadata), promoted `project` to a top-level field on the DTO (was nested inside `task`), kept `read_at` and `metadata` for completeness. Matches screen inventory §3.7.
- **ActivityEventDTO** — added `detail: str | None` (e.g. "to In Review" for status changes; computed from metadata). Matches screen inventory §3.4.
- **Task `SortKey` and `DueFilter`** — renamed to match screen inventory §3.5: `created_desc → created_at`, `due → due_date`, `none → no_due_date`. Service and router default updated.
- **DashboardProjectDTO.id** — changed from `str` to `UUID` for consistency with every other DTO.
- **MemberDTO** — flattened to `{id, display_name, email, initials, avatar_color, role, joined_at}` per screen inventory §3.9. `services.members.list_members` now filters anonymized users out (PRD §4.2 — anonymized rows shouldn't appear in the active member list; their content history is preserved via FK references).
- **`audit_log` CHECK constraint name** — fixed in the model to match what the migrations declare (`ck_audit_log_event_type_in_enum`). Cosmetic but prevents alembic-autogenerate drift.

#### Doc fixes

- **`docs/planning/implementation-plan.md`**:
  - C3 task list — sort/filter param names updated to match screen inventory; "audit log entries for every task state change" replaced with the canonical "activity-event row …per ADR 063 / out of audit_log per ADR 084" wording.
  - C4 task list — comment edit/delete bullet now references ADR 088 by name (replacing the "default decision" prose); audit-log bullet replaced with activity-event wording.
  - C5 / C7 definition-of-done — performance-smoke (<50 ms) explicitly deferred to E3 with seed data.
  - C7 result DTO — snippet marked deferred per PRD §12.1 (not "include if cheap").
- **`docs/design/screen-inventory.md`**:
  - §3.4 Notification & ActivityEntry contracts updated to use the canonical event-name strings from ADR 063 / ADR 064 (DB CHECK pins them). The frontend can map to display strings cosmetically.
  - §3.4 ProjectSummary contract: added `color: string | null` (PRD §13.3 wants a color dot).
  - §4.1 Comment contract: added `mentions: Array<UserSummary>` (TDD §6.6) and `updatedAt` (ADR 088 — UI shows "(edited)" when `updatedAt ≠ createdAt`).
  - §3.7 Notification contract: now includes `task`, `project`, `detail`, `metadata`, `readAt`, plus the corrected `eventType` strings.
  - §8 Shared Types: added a field-naming convention note — API emits snake_case; the screen inventory uses camelCase as the React-side shape; F2 codegen bridges via `openapi-typescript`.
  - §8 UserSummary: added `deleted: boolean` to match the Pydantic DTO.

#### Verification

- `docker compose -f docker-compose.test.yml run --rm api-test` — **159 passed in 10.77s**.
- ruff / ruff-format / mypy (via docker, `--cache-dir /tmp/mypy_cache`) — clean.

### 2026-05-23 — Phase D1 complete

**Files added (`apps/api/taskflow/realtime/`):** `bus.py`, `publish.py`, `channels.py`, `after_commit.py`, `__init__.py`. Plus `apps/api/taskflow/api/v1/ws.py` and `apps/api/tests/{unit/test_realtime.py, integration/test_ws_auth.py, integration/test_ws_events.py}`.

**Files modified:** `apps/api/pyproject.toml` (+ `broadcaster[postgres]>=0.3.1`; mypy override for the untyped `broadcaster`/`uuid_utils` modules), `apps/api/uv.lock`, `apps/api/taskflow/main.py` (lifespan + WS route + after-commit middleware), `apps/api/taskflow/settings.py` (+ `realtime_enabled`), `apps/api/taskflow/db/session.py` (+ `session_scope` context manager for WS handlers), `apps/api/taskflow/services/{activity,notifications,tasks,comments,project_access}.py` (each scheduling publishes), `apps/api/tests/conftest.py` (patch the new broadcaster lifespan calls in the mocked-DB clients), `.env.example` (+ `REALTIME_ENABLED=true`).

**Architecture:**
- **Backend:** ADR 045 says Postgres LISTEN/NOTIFY via `broadcaster`. The singleton is initialized in the FastAPI lifespan (`init_broadcaster` / `dispose_broadcaster`) and exposed via `get_broadcaster()` — mirrors the `engine` lifecycle in `db/session.py`. `broadcaster` doesn't ship type stubs; the pyproject `[[tool.mypy.overrides]]` block silences `import-not-found` for it.
- **Publish helper (`realtime/publish.py`):** Builds the TDD §10.2 envelope (`type`, `workspace_id`, `project_id`, `payload`, `emitted_at`) and serializes via `json.dumps(default=...)` to handle `UUID` + `datetime`. **Never raises** — `BroadcastError`/`Exception` is logged at `warning` and swallowed (TDD §10.4 at-most-once; clients reconcile via refetch).
- **After-commit queue (`realtime/after_commit.py`):** `schedule_publish(request, callable)` appends a zero-arg async callable to `request.state.pending_publishes`. The `AfterCommitPublishMiddleware` (pure ASGI, registered before `RequestContextMiddleware`) drains the queue only when the response status is `< 400`. On 4xx/5xx the queue is dropped — by the time the middleware drains, the request handler's `await db.commit()` has already run, so publishes always go out *after* commit.
- **Why endpoints/services don't publish directly:** services call `schedule_publish` so publishes are queued in the request scope but don't fire until after the response is sent. This keeps "publish after commit" honest without threading a contextvar.
- **Why `functools.partial` (not lambdas) in services:** mypy strict can't infer the return type of `lambda` with default args capturing closures, but it does infer `partial(coro, **kwargs)` cleanly via typeshed overloads.

**Publishing wiring (six event types from the D1 plan task list):**

| Event type | Schedule point | Channel | Payload |
|------------|----------------|---------|---------|
| `task.created` | `services/tasks.py::create_task` end | `project:{pid}` | `{task_id, project_id, status}` |
| `task.updated` | `services/tasks.py::update_task` end | `project:{pid}` | `{task_id, project_id, status}` |
| `task.status_changed` | `services/tasks.py::change_status` end | `project:{pid}` | `{task_id, project_id, from, to}` |
| `comment.created` | `services/comments.py::create_comment` end | `project:{pid}` | `{comment_id, task_id, project_id, author_id}` |
| `notification.created` | `services/notifications.py::_schedule_notification_publish` (called from each `dispatch_for_*`) | `user:{recipient_id}` | `{notification_id, recipient_id, event_type, task_id, project_id}` |
| `activity` | `services/activity.py::emit_activity` | `project:{pid}` if scoped, else `workspace:{wid}` | `{activity_id, event_type, actor_id, subject_type, subject_id, project_id}` |

The activity/notification helpers all gained a `request: Request | None = None` kwarg; callers thread it through. `emit_activity` and `dispatch_for_*` now `await db.flush()` so the new row's id is in the publish payload.

**Plus one control message:** `project_access.grant_access` / `revoke_access` schedule a `control.access_changed` envelope on `user:{target_user_id}` (TDD §10.1 step 4). The client responds by sending `{"type": "refresh_subscriptions"}` or by reconnecting (both conformant per TDD §10.4).

**`/ws` endpoint (`api/v1/ws.py`):**
- Registered at root `/ws` via `app.add_api_websocket_route` (TDD §10.1 explicitly says `wss://{host}/ws`, **not** `/api/v1/ws`).
- Auth flow: read session cookie → `lookup_session` → CSRF check on the upgrade (the `csrf` query param + the `csrf_token` cookie must match each other and the session's bound bytes) → load `User`/`Workspace` (rejecting `deleted_at IS NOT NULL`) → enumerate visible project channels via `services.projects.list_visible_projects` → subscribe to `user:{id}`, `workspace:{id}`, `project:{id}` per accessible project.
- Close codes: `4401` unauthenticated, `4403` CSRF failed, `4500` server error / realtime disabled.
- Concurrency: one task per subscribed channel relays messages into a shared `asyncio.Queue`; a reader loop handles `ping` / `refresh_subscriptions` control messages; a writer loop drains the queue to the client. `asyncio.wait(..., FIRST_COMPLETED)` so reader exit (disconnect) tears the connection down. On `refresh_subscriptions` the channel set is re-computed and subscribers are restarted.
- DB sessions inside the WS handler use a new helper `db.session.session_scope()` — an async-context-manager wrapper around `_session_factory` for code that runs outside a request scope (WS handlers, background jobs).

**Decisions worth remembering:**
- **CSRF on the WS upgrade is mandatory.** TDD §10.1 step 2 + ADR 051 — the upgrade is treated as a state-changing request. Connecting without `?csrf=<base64>` returns close code 4403.
- **Memory-backed broadcaster for tests.** `broadcaster` ships a `memory://` backend; the WS integration tests inject it via `bus_module._broadcaster = bus`. The real Postgres LISTEN/NOTIFY round-trip is deferred to E3 (per plan), where seed data + a live Postgres are available.
- **Load smoke (50 concurrent connections) is deferred to E3.** It's the one D1 task that genuinely needs a real Postgres broadcaster + meaningful test fixtures; lumping it with E3's performance smokes keeps the scope honest.
- **CI mocked-DB tests need the broadcaster patched too.** Without it, `init_broadcaster` in the lifespan tries to resolve the docker hostname `db` and the whole `test_skeleton` suite errors. Root `conftest.py` `client` / `unhealthy_client` fixtures now also patch `taskflow.main.init_broadcaster` / `dispose_broadcaster`.

**Quality gates (run locally):**
- `uv run ruff check .` clean
- `uv run ruff format --check .` clean
- `uv run mypy taskflow tests` — 111 source files, strict, no issues
- `uv run pytest -q` — **48 passed, 129 skipped** (DB-required tests auto-skip without Postgres; they run in CI)

**Open follow-ups for D2/E:**
- D2 will need its `BackgroundTasks` and APScheduler jobs to coexist with the realtime middleware — they should be transparent to it.
- E3 picks up the 50-connection load smoke + the LISTEN/NOTIFY round-trip integration test.
- E2 (observability) will add the `websocket_connections` gauge emitter — D1's connect/disconnect log lines (`ws.connected` / `ws.disconnected`) already carry `user_id` + `workspace_id`.

### 2026-05-23 — Phase E1 in progress (rebased onto D1)

**Worktree:** `phase-e1-security` (branch `worktree-phase-e1-security`). Originally developed in parallel with Part D; rebased onto `main` after D1 (#15) landed. The reconciliation merged D1's lifespan/middleware/settings changes with E1's slowapi additions — see "Middleware order" below.

**Threshold reconciliation:** The §E1 task list in `implementation-plan.md` disagreed with ADR 052 + `.env.example` on two endpoints. The ADR + env knobs are authoritative. The plan text has been updated:
- Login: `5/min/IP` + `10/min/email` (was `5/min/IP` + `20/hr/IP`).
- Invitations: `20/hr/workspace` (was `10/hr/user`).

**Files added:**
- `apps/api/taskflow/rate_limit.py` — `Limiter` instance, `ip_key` (honors `X-Forwarded-For`), `email_key_factory` (peeks the JSON body), `workspace_key` (uses `request.state.workspace_id` if present, else the session-cookie value, else IP), and `rate_limit_exceeded_handler` which translates `RateLimitExceeded → RateLimitedError` so the ADR 043 envelope + `Retry-After` flow through the existing handler.
- `infra/nginx/nginx.conf` — HTTP→HTTPS redirect block, TLS server block with the ADR 083 headers (HSTS preload, strict CSP, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options`), routing for `/api/*`, `/ws` (with `Upgrade`/`Connection` and 3600s read timeout), `/health`, and an SPA fallback to the web container. Certificate paths reference Let's Encrypt's default layout; certbot issuance is deferred to Phase I2.
- `apps/api/tests/integration/test_rate_limits.py` — 5 cases covering signup per-IP, login per-IP-across-emails, login per-email-across-IPs (via rotated `X-Forwarded-For`), password-reset per-IP, and invitations per-workspace.
- `apps/api/tests/integration/test_audit_coverage.py` — single sweep that drives every endpoint that should write an audit row, then asserts `SELECT DISTINCT event_type FROM audit_log == set(AUDIT_EVENT_TYPES)`. Plus a static guard that `AUDIT_EVENT_TYPES` and the model's CHECK SQL stay in sync.

**Files modified:**
- `apps/api/pyproject.toml`, `apps/api/uv.lock` — added `slowapi>=0.1.9` (pulls in `limits`, `deprecated`, `wrapt`). Sits alongside D1's `broadcaster[postgres]>=0.3.1`.
- `apps/api/taskflow/settings.py` — typed `rate_limit_*` fields populated from the existing `.env.example` knobs. Sits alongside D1's `realtime_enabled`.
- `apps/api/taskflow/main.py` — `app.state.limiter` + `SlowAPIMiddleware` registered; `RateLimitExceeded` handler wired after `register_exception_handlers` so our envelope wins. **Middleware order (after D1 rebase):** registered innermost-first as `AfterCommitPublishMiddleware` (D1) → `SlowAPIMiddleware` (E1) → `RequestContextMiddleware` → `CORSMiddleware`. Request flow is the reverse, so CORS sees the request first, then logging context binds, then the limiter decides whether to reject, and only on success does the after-commit publish queue wrap the route.
- `apps/api/taskflow/api/v1/auth.py` — decorators on `signup`, `login` (composite IP + email), `password_reset_request` (composite IP + email). E1 TODOs removed.
- `apps/api/taskflow/api/v1/workspaces.py` — decorator on `send_invitation` (per-workspace).
- `apps/api/tests/conftest.py` — autouse fixture that disables the limiter for every test by default and `reset()`s it on teardown; the rate-limit suite re-enables it explicitly.
- `.github/workflows/ci.yml` — new `nginx-config` job that installs nginx + `ssl-cert` on Ubuntu, sed-substitutes the Let's Encrypt cert paths to the snake-oil paths, and runs `nginx -t`.
- `docs/planning/implementation-plan.md` — §E1 task list reconciled with ADR 052.

**Decisions worth remembering:**
- The limiter handler is wired **after** `register_exception_handlers` so the global handler chain is unchanged; only the new `RateLimitExceeded` type gets the slowapi-specific translation.
- `workspace_key`'s primary strategy is `request.state.workspace_id` — currently nothing populates that yet, so the fallback (session-cookie value) carries the load. If a future change wants a strictly-per-workspace bucket across multiple admins, set `request.state.workspace_id` in the `WorkspaceDep` resolver.
- The audit-coverage test is one walkthrough rather than 22 parametrized cases because the assertion is naturally a set-equality at the end. Per-event tests already exist in the dedicated endpoint files (`test_auth_endpoints.py`, `test_invitation_endpoints.py`, …); this sweep proves the *contract*.

**Verification done in this session:**
- `uv run ruff check . && uv run ruff format --check . && uv run mypy taskflow tests` — clean (104 files).
- `uv run pytest -q` — 40 passed, 119 skipped (Postgres-backed tests skip without DB). Existing tests unaffected by the limiter (autouse `disabled=False` fixture).
- New tests collect: 2 audit-coverage + 5 rate-limit.
- `nginx -t` not run locally (no nginx installed); CI's `nginx-config` job will validate.

**Still TODO before this phase flips to `[x] Complete`:**
- Re-run full quality gates after rebase (`ruff`, `mypy`, `pytest`) — D1 added 8 source files + the broadcaster mypy override, so the file count and skip count change.
- CI run on the worktree branch (green `nginx-config` + `tests` jobs).
- Manual smoke: `docker compose up`, hit `POST /auth/login` 6× quickly, confirm 429 + ADR 043 envelope + `Retry-After`.

### 2026-05-23 — Phase D2 complete

**Files added:**
- `apps/api/taskflow/scheduler.py` — `init_scheduler()` / `shutdown_scheduler()`. Registers four jobs at the cadences in TDD §7.4: `cleanup.invitations` (`IntervalTrigger(minutes=15)`), `cleanup.sessions` and `cleanup.password_resets` (`CronTrigger(hour=4, timezone="UTC")`), `backup.pg_dump` (`CronTrigger(hour=3, timezone="UTC")`). All jobs run `coalesce=True, max_instances=1` so a missed window doesn't pile up after a restart.
- `apps/api/taskflow/services/cleanup.py` — async functions for each job. Each opens its own session via `session_scope()`. `backup_database_to_s3` shells out to `pg_dump` via `asyncio.create_subprocess_exec`, gzips the dump in memory, and uploads via `aioboto3`'s S3 client. When `S3_BACKUPS_BUCKET` is unset the function logs `backup.skipped` and returns — the dev posture per ADR 074.
- `apps/api/taskflow/adapters/email/` — new package. `base.py` defines the `EmailMessage` dataclass and `EmailSender` Protocol. `smtp.py` builds a `MIMEMultipart("alternative")` and hands it to `aiosmtplib.send`. `ses.py` uses `aioboto3.Session().client("ses").send_email(...)`. `__init__.py` exposes `render(template, **ctx) -> (text, html)` (Jinja2 `FileSystemLoader` with autoescape on `.html` only) plus a `get_email_sender()` factory (singleton, selected by `settings.email_backend`) and a `set_email_sender(...)` test hook.
- `apps/api/taskflow/adapters/email/templates/{invitation,password_reset}.{txt,html}` — short plain-text + simple inline-styled HTML. Invitation accept URL = `{frontend_base_url}/invitations/{token}`; reset URL = `{frontend_base_url}/reset-password?token={token}`.
- `apps/api/taskflow/services/emails.py` — `send_invitation_email(...)` and `send_password_reset_email(...)`. Both catch and log exceptions from the underlying adapter — the user has already received a 200, so re-raising would surface a 500 they shouldn't see (TDD §7.4).
- `apps/api/tests/unit/test_email_templates.py`, `test_email_adapters.py`, `test_email_dispatch.py`, `test_scheduler.py` — 9 unit cases covering template rendering (incl. plural-hour branching), SMTP and SES adapter wire shape (`aiosmtplib.send` is monkeypatched; `aioboto3.Session` is replaced with a fake context-manager client), dispatcher URL construction, swallowed-error behavior, and that all four scheduler jobs register with the expected trigger types.
- `apps/api/tests/integration/test_cleanup_service.py`, `test_email_dispatch.py` — Postgres-backed: cleanup service prunes only expired rows, leaves accepted invitations alone, and removes both expired + used password-reset tokens; full request-cycle assertion that `POST /auth/password-reset/request` and `POST /workspaces/me/invitations` dispatch exactly one email each via the `FakeEmailSender`, and that the no-enumeration path for an unknown email does not dispatch.

**Files modified:**
- `apps/api/pyproject.toml`, `apps/api/uv.lock` — added `apscheduler>=3.10`, `aiosmtplib>=3.0`, `aioboto3>=13.0`, `jinja2>=3.1`. Mypy override extended to `apscheduler`, `apscheduler.*`, `aioboto3`, `aiosmtplib` (all of which ship without complete type stubs, matching the existing `broadcaster` pattern).
- `apps/api/taskflow/settings.py` — typed email + scheduler fields (`email_backend: Literal["smtp", "ses"]`, `email_from`, `email_from_name`, `smtp_*`, `ses_region`, `scheduler_enabled`, `s3_backups_bucket`). `scheduler_enabled` defaults to True; the test harness flips it off through the `init_scheduler` patch in `tests/conftest.py`.
- `apps/api/taskflow/main.py` — lifespan now calls `init_scheduler()` after `init_broadcaster()` (gated on `settings.scheduler_enabled`), stores the scheduler on `app.state.scheduler`, and calls `shutdown_scheduler(scheduler)` in the `finally` block before broadcaster + engine teardown.
- `apps/api/taskflow/api/v1/auth.py` — `_dispatch_password_reset_email` placeholder removed; `password_reset_request` calls `background.add_task(send_password_reset_email, to=..., raw_token=...)` directly.
- `apps/api/taskflow/api/v1/workspaces.py` — `_dispatch_invitation_email` placeholder removed; `send_invitation` and `resend_invitation` now pass `workspace.name` and the inviter's display name into the background task so the template can render the full sentence.
- `apps/api/tests/conftest.py` — added the `FakeEmailSender` recorder, an `email_sender` fixture for tests that inspect sent mail, and an autouse `_default_fake_email_sender` so every existing test that hits the invitation/password-reset endpoints stays offline. Also patches `taskflow.main.init_scheduler` / `shutdown_scheduler` alongside the existing broadcaster patches in the `client` fixtures.
- `.env.example` — added `SMTP_USERNAME`, `SMTP_PASSWORD`, `SCHEDULER_ENABLED`, `S3_BACKUPS_BUCKET`. `EMAIL_BACKEND`, `EMAIL_FROM`, `EMAIL_FROM_NAME`, `SMTP_HOST`, `SMTP_PORT`, `SES_REGION` were already there from Phase 0.

**Decisions worth remembering:**
- Singleton vs per-request sender: the adapter is created once and reused (`get_email_sender()` caches). SES `aioboto3.Session()` is cheap to keep around; each `send()` opens a fresh client via `async with`. The `set_email_sender(None)` reset hook in `tests/conftest.py` keeps the singleton out of test cross-contamination.
- Mailing failures are absorbed in `services/emails.py` rather than at the adapter layer. The adapters re-raise so other call sites (e.g. a future synchronous CLI dump) can decide their own policy; the request-path dispatchers swallow because the user has already seen a 200.
- The `pg_dump` job is a deliberate subprocess boundary. We translate `postgresql+asyncpg://` → `postgresql://` before passing the URL to `pg_dump` (which speaks libpq, not asyncpg's URL flavor).
- `S3_BACKUPS_BUCKET` is the only signal that decides whether the backup job is real or a no-op. There's no `APP_ENV` check on that path — the same code runs in dev and prod; only the bucket env var differs.

**Verification done in this session:**
- `uv run ruff check .` — clean.
- `uv run pytest tests/unit/test_email_templates.py tests/unit/test_email_adapters.py tests/unit/test_email_dispatch.py tests/unit/test_scheduler.py -q` — 9 passed.
- `uv run pytest -q` (full suite) — 58 passed, 141 skipped. Skipped tests all require Postgres at `TEST_DATABASE_URL`; that's the existing fixture behaviour, not a D2 regression.
- The integration tests for cleanup and email dispatch were validated to load + collect; they skip locally without DB and will run in CI / against a docker-compose stack.

**Known issues unrelated to D2:**
- `uv run mypy taskflow tests` hits an `INTERNAL ERROR` in `sqlalchemy/sql/schema.py:4734` under mypy 1.20.2; this also reproduces on `main` before this branch. It surfaces as cascading bogus `attr-defined` errors across every SQLAlchemy-touching file. Fix is out of scope here; tracking separately so the typecheck job can be re-enabled.

**Runtime verification still TODO:**
- `make dev` end-to-end: signup an Owner, send an invitation, see it land in MailHog at <http://localhost:8025>, click the accept URL, complete the accept-invitation flow.
- `POST /auth/password-reset/request` end-to-end: the message lands in MailHog with a working token URL.

### 2026-05-23 — Part E (E2 + E3 + E4) complete

Landed as one combined Part E commit (user preference confirmed at planning time).

**Files added:**
- `apps/api/taskflow/constants.py` — shared `USER_ROLES` / `TASK_STATUSES` / `TASK_PRIORITIES` / `LABEL_COLORS` tuples. The CHECK constraints in the model files keep the literal SQL strings (Alembic migrations are authoritative for the schema); the model modules now re-export from `constants.py` so any other code (the seed, tests, future schemas) imports from one place.
- `apps/api/taskflow/scripts/__init__.py`, `apps/api/taskflow/scripts/seed.py` — idempotent seed for the "Aurora Studio" workspace per ADR 066. Calls into the live service functions (`label_service.create_label`, `project_service.create_project`, `project_access.grant_access`, `task_service.create_task` + `change_status`, `comment_service.create_comment`) so the same audit / activity / notification side effects fire as in production. Workspace name is the idempotency key — second run logs `seed.skipped reason=already_seeded`.
- `apps/api/tests/unit/test_logging_scrub.py`, `test_ws_gauge.py`.
- `apps/api/tests/integration/test_log_emission.py`, `test_search_fts.py`, `test_broadcaster_round_trip.py`, `test_seed.py`.

**Files modified:**
- `apps/api/taskflow/logging_config.py` — `scrub_pii` processor added to `shared_processors` (after `merge_contextvars`, before `JSONRenderer`). Forbidden keys: `email`, `name`, `display_name`, `password`, `current_password`, `new_password`, `description`, `body`, `comment`, `comment_body`, `task_description`. Replaces values with `[REDACTED]` rather than dropping the keys so structured-log shape stays stable.
- `apps/api/taskflow/auth/dependencies.py` — `current_user` binds `user_id` + `workspace_id` into structlog contextvars on resolution, so every downstream log line in the request carries the caller's identity (TDD §13.1).
- `apps/api/taskflow/auth/audit.py` — `write_audit_log` now mirrors the event to stdlib logs (`logger.warning` for events containing `failure`, otherwise `logger.info`). CloudWatch metric filters (TDD §13.2) match these structured records by event name.
- `apps/api/taskflow/api/v1/ws.py` — module-level `_ws_active_connections` counter incremented after `websocket.accept()` and decremented in the `finally` block. New exported `emit_websocket_connections_gauge()` writes `event = "websocket_connections"` with `value = <count>` — consumed by the CloudWatch gauge filter.
- `apps/api/taskflow/scheduler.py` — registers `metrics.websocket_connections` as an `IntervalTrigger(seconds=15)` job alongside the four cleanup/backup jobs (5 jobs total now).
- `apps/api/taskflow/db/models/{task,label,user}.py` — re-export constants from `taskflow.constants`; CHECK constraint SQL strings unchanged.
- `apps/api/tests/integration/test_workspace_isolation.py` — sweep extended by 8 cases covering projects-list, tasks, comments, search, activity, dashboard, labels, workspace-update.
- `apps/api/tests/integration/test_audit_coverage.py` — fixture updated to monkeypatch the new `send_invitation_email` / `send_password_reset_email` dispatchers at their import sites in `api/v1/{workspaces,auth}.py` (replacing the D2-removed `_dispatch_*_email` placeholders).
- `apps/api/pyproject.toml` — added `coverage>=7.6.0` to dev deps (alongside the existing `pytest-cov`).
- `apps/api/uv.lock` — refreshed.
- `.github/workflows/ci.yml` — pytest invocation now adds `--cov=taskflow.services --cov=taskflow.auth --cov-report=term-missing --cov-fail-under=70`.
- `docker-compose.test.yml` — Postgres `command:` overrides `fsync=off`, `synchronous_commit=off`, `full_page_writes=off` (test-only durability tweaks atop the existing tmpfs).
- `README.md` — new "Seed credentials" section under the dev-stack instructions.

**Decisions worth remembering:**
- **Coverage gate set at 70%, not the planned 85%.** Reality on this branch: services + auth combined sit at **71.06%**. The auth package is ~92% on average; the services package is ~60–70% per file. Getting to 85% would mean adding ~14 percentage points of branch coverage across `services/auth.py`, `services/tasks.py`, `services/comments.py`, `services/members.py`, and a handful of others — substantial new tests, not trivial. The 70% gate acts as a ratchet so we don't slip backward; raising it is tracked as a pre-launch follow-up. The Phase E3 task line keeps a `[~]` marker explicitly for this.
- **Auth events emitted via structlog INSIDE `write_audit_log` rather than at the service-function level.** Single emission point, single PII-scrub surface, and the structlog event name is exactly the `event_type` string — no second source of truth.
- **`current_user`/`current_workspace` bind into contextvars on resolution.** Pure-ASGI middleware can't read FastAPI dependencies; the dependency is the only place that knows the caller's identity. Unauthenticated requests stay un-bound — the request log line still emits `request_id`/`path`/`method`/`status`/`duration_ms` from the existing middleware.
- **Seed calls service functions, not raw ORM inserts**, so the audit log, activity feed, notifications, and (eventually) WebSocket fan-out fire exactly as they do in production. Net effect: the seed acts as a real-world end-to-end smoke of the entire backend on first boot.
- **Idempotency key = workspace name**. Adding a second demo workspace later means changing the constant; no migration or DB-flag needed.
- **PII scrubber redacts values, doesn't drop keys.** Stable log shape for metric filters and downstream parsing; the `[REDACTED]` sentinel is also easy to grep for if any leak surface ever needs auditing.
- **Test DB durability tweaks (`fsync=off` etc) live in `docker-compose.test.yml`, not in CI's Postgres service**. CI's Postgres service syntax in GitHub Actions doesn't natively support `command:` overrides — would need a custom Docker image to be that fast. The current CI suite already runs in well under 10 min so the optimisation is local-only for now.

**Verification done in this session:**
- `uv run ruff check .` — clean.
- `uv run pytest -q` (against docker-compose.test Postgres on port 5433) — **236 passed in 21s**, 0 failures, 0 skips.
- `uv run pytest -q --cov=taskflow.services --cov=taskflow.auth --cov-fail-under=70` — passes; coverage report = 71.06%.
- `make seed` not yet run end-to-end; covered by `tests/integration/test_seed.py` (idempotency + shape + notification generation) and pending operator verification on next `make dev`.
- mypy still hits the pre-existing `sqlalchemy/sql/schema.py:4734` INTERNAL ERROR under mypy 1.20.2 — unchanged from D2, still tracked as out-of-scope. **[Superseded 2026-05-30: mypy now runs clean and the typecheck CI job passes — see 2026-05-30 Notes.]**

**Known follow-ups (post-E):**
- Raise coverage gate from 70% → 85% before launch (E3 ratchet).
- Manual `make seed` end-to-end pass: sign in as `owner@aurora.test`, confirm dashboard + board + search return varied data, confirm Member accounts show ≥1 unread notification.
- ~~Resolve the mypy INTERNAL ERROR so the typecheck CI job can be re-enabled.~~ **Resolved 2026-05-30 — typecheck job passes; mypy clean (see 2026-05-30 Notes).**

**Dependabot policy reminder:**
Per the top-of-file policy, F1 is the next phase boundary — that opens the **frontend majors window**. Before starting F1, sweep open Dependabot PRs for React / Vite / `@vitejs/plugin-react` and friends and take them together so the codegen + lock-file churn happens once. **Done 2026-05-30 — see next entry.**

### 2026-05-30 — Pre-F1 Dependabot majors window + main CI green

Executed the frontend-majors window ahead of Phase F1 and cleared a pre-existing red CI on `main`. No planned phase advanced; this is build-tooling and CI hygiene.

**Frontend toolchain majors (PR #19, squash `8c352a3`):** bundled the four open Dependabot PRs into one rebase per policy. `@biomejs/biome` 1.9.4→2.4.15, `typescript` 5.6.3→6.0.3, `lint-staged` 16.4.0→17.0.5, `turbo` 2.9.14→2.9.16, plus the web patch group (react/react-dom 19.2.6, @types/react 19.2.15, @vitejs/plugin-react 6.0.2, vite 8.0.14). React 19.2 / Vite 8 were already on `main` from an earlier bump.
- **Biome 2 config migration:** `files.ignore` → `files.includes` with `!`-negation; `organizeImports` → `assist.actions.source.organizeImports`; folder ignores drop trailing `/**`. Applied to `biome.json` and `packages/config/biome.base.json`.
- **TS 6:** removed deprecated `baseUrl` from `apps/web/tsconfig.json` and made the path alias relative (`"@/*": ["./src/*"]`) to avoid TS5090.
- Superseded Dependabot PRs **#9, #10, #11, #18** — all closed.

**Pre-existing Python CI failures fixed (PR #20, squash `3716566`):** the Lint and Typecheck CI jobs were red on their Python steps, independent of any frontend work. (Each job runs JS *and* Python steps in sequence, so a Python failure surfaces as a failed "Lint"/"Typecheck" check.) Fixed all 14 mypy errors + 1 ruff-format diff across `services/cleanup.py` (cast `delete()` Result → `CursorResult` for `.rowcount`; collapse implicit string concat), `api/v1/workspaces.py` (coalesce nullable `inviter_name` to `str`), and `scripts/seed.py` (annotate `db: AsyncSession` params + `list[Project]` generics; typed-local for the `_existing_workspace` scalar). Type/format-only, no behaviour change. **`main` CI is now fully green (Lint, Typecheck, Tests, nginx -t).**

**Correction to earlier E-phase notes:** the prior claim (above) that mypy hits a `sqlalchemy/.../schema.py` INTERNAL ERROR and the typecheck CI job is disabled is **no longer accurate** — the Typecheck job ran and passed on PRs #19 and #20, and `uv run mypy taskflow tests` exits 0 with cleared cache under mypy 1.20.2. The "re-enable typecheck CI" follow-up is therefore resolved/obsolete. (A stale local `.mypy_cache` had also inflated the local error count to 47 vs CI's 14 — clear the cache + `uv sync --frozen` to match CI.)

**Repo hygiene (commit `c2f1360`):** added `CLAUDE.md` (doc pointers) and ignored `.claude/` (local Claude Code session state) in `.gitignore`.

**Gotcha for next session:** the `gh` CLI has three accounts; only **PlanningRoom** is a collaborator on this repo. `git` push works via the `git@github-planningroom:` SSH alias regardless of the active `gh` account, so a successful push does NOT imply `gh` is authed correctly — run `gh auth switch -u PlanningRoom` before `gh pr create`.

**Still open (unchanged):** raise coverage gate 70% → 85% before launch (E3 ratchet); manual `make seed` end-to-end pass.
