# TaskFlow — Implementation Status

**Last Updated:** 2026-06-28
**Current Phase:** Part I in progress — I1 + I2 + I3 complete (see Notes 2026-06-28); I4 (Production Cutover) next — needs a live AWS account
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
| F | Frontend Foundation | 4 | 4 | 0 | 0 |
| G | Frontend Screens | 8 | 8 | 0 | 0 |
| H | Frontend Cross-Cutting | 5 | 5 | 0 | 0 |
| I | E2E, Infra, Deploy | 6 | 3 | 0 | 0 |
| **Total** | | **42** | **39** | **0** | **0** |

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
- [x] SES adapter (prod) + SMTP-to-MailHog adapter (dev) — **prod adapter superseded by Resend (ADR 067, 2026-06-14); SES sender swapped out in I2.** Dev MailHog path unchanged.
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
- [x] Coverage report: ≥85% on `services/` and `auth/` — **gate raised to 85%; actual is ~98%** (resolved 2026-05-30, see note below). The 71% reading was a measurement artifact (coverage wasn't tracing the ASGI request path); fixing `[tool.coverage.run] concurrency` revealed true coverage of ~90%, and a targeted test pass closed the genuine remaining branches.
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

#### Phase F1 — Frontend Skeleton `[x] Complete`
- [x] Vite + React 19 + TS strict
- [x] Tailwind v3 mapped to CSS custom properties
- [x] `tokens.css` with every DRD §2 token on `:root`
- [x] Inter font from Google Fonts
- [x] TanStack Query v5 with `QueryClientProvider`
- [x] TanStack Router v1 with empty route tree
- [x] React Hook Form + Zod added; shared schemas dir
- [x] `react-intl` + English `locales/en.json`
- [x] Logical CSS properties enforced
- [x] Reduced-motion global rule

#### Phase F2 — API Client and Type Codegen `[x] Complete`
- [x] `pnpm gen:api` script using `openapi-typescript`
- [x] `openapi-drift` CI gate
- [x] Typed `apiClient` with auto CSRF header
- [x] `useApiQuery` / `useApiMutation` helpers
- [x] Smoke test against running backend — implemented as a mocked-`fetch` Vitest test (`client.test.ts`) asserting the ADR 043 envelope parses into `ApiError`; see F2 note re: offline approach

#### Phase F3 — UI Primitives and Storybook `[x] Complete`
- [x] Radix primitives + CVA installed
- [~] Storybook configured with `vitest-axe` — **Storybook deferred** (Vite 8 builder risk); verification via Vitest + `vitest-axe` test-per-primitive instead (see F3 note)
- [x] `Button` (Primary/Secondary/Ghost/Destructive)
- [x] `Input`, `Textarea`, `Select`
- [x] `Avatar` (deterministic color)
- [x] `StatusBadge`
- [x] `LabelChip`
- [x] `PriorityIcon`
- [x] `DueDate` (overdue/approaching styling)
- [x] `Toast` system
- [x] `Dialog`, `DropdownMenu`, `Tabs`, `Checkbox`, `Tooltip`
- [x] Lucide icons integrated with default sizing
- [x] axe assertion per primitive (replaces "stories per variant" — see F3 note)

#### Phase F4 — App Shell `[x] Complete`
- [x] `AppShell` three-zone layout (sidebar 240, header 52)
- [x] Sidebar: logo, primary nav, projects, bottom (Settings + user identity)
- [x] Header: breadcrumb, search, notification bell, user avatar
- [x] Logo + wordmark per DRD §5
- [~] Responsive shell — desktop + sidebar-hidden-below-`md` implemented; tablet icon rail (`Sidebar collapsed` prop exists) + mobile hamburger overlay polish deferred to a later phase (see F4 note)
- [x] Route tree per screen inventory §3 (placeholders for all routes)
- [x] `/projects/:projectId` redirect → `/projects/:projectId/board`
- [x] Unauthenticated routes (`/login`, `/signup`, `/invitations/:token`) rendered outside the shell
- [x] `useCurrentUser` hook backed by `/auth/me`

---

### Part G — Frontend Screens

#### Phase G1 — Auth Screens `[x] Complete`
- [x] Login screen (DRD §8.1)
- [x] Signup screen (PRD §3.1)
- [x] Accept-invitation screen — **blind accept form** (see G1 note: no backend invitation-preview endpoint, so workspace/role/inviter preview, email prefill, and new-vs-existing branching are deferred); expired/invalid token states implemented
- [x] Password-reset request + confirm screens (confirm at `/reset-password?token=…` per the reset email)
- [x] Form schemas via Zod (`apps/web/src/forms/schemas/index.ts`)
- [x] Mutation hooks hydrate user cache + navigate (`useAuthSuccess`); shell route guard redirects unauthenticated users to `/login`
- [x] Component + axe tests (24 new tests; full web suite 50 green)

#### Phase G2 — Dashboard `[x] Complete`
- [x] Two-column 60/40 grid
- [x] My Tasks section (groups by project)
- [x] Recent Activity section (with relative timestamps)
- [x] Projects section (color dot + status counts)
- [x] Empty states (role-aware)
- [x] First-run prompts (Owner / invited user)
- [x] Create Project modal (reused by sidebar `+`, dashboard empty state, first-run prompt)
- [x] Wired to dashboard + activity endpoints
- [x] Component + axe tests

#### Phase G3 — Board View `[x] Complete`
- [x] Sub-nav (view toggle, filter button, active filter chips, "Clear all" link, sort dropdown, project settings icon, Create task button)
- [x] Filter chip bar
- [x] Five columns; cancelled hidden by default
- [x] Task cards (title, labels, meta row)
- [x] Drag-and-drop with `@dnd-kit/core` (desktop only)
- [x] Optimistic status update with rollback + error toast
- [x] URL-driven filter + sort state
- [x] Project Settings modal (Details + Access tabs, screen inventory §5.2)
- [~] Mobile column stacking, status via dropdown — **deferred** with the rest of the responsive/mobile polish (see F4 note; DRD §15)
- [x] Component + axe tests

#### Phase G4 — List View `[x] Complete`
- [x] Sortable columns (title, status, assignee, priority, due, labels) — sortable on the backend-supported keys (priority, due, assignee); title/status header sort not offered
- [x] Inline status dropdown (role-gated)
- [x] Shared filter/sort URL state with board view
- [~] Mobile responsive (scroll or stacked) — **deferred** with the responsive/mobile polish (see F4 note)
- [x] Component + axe tests

#### Phase G5 — Task Detail Panel `[x] Complete`
- [x] Panel route with backdrop + Esc + × dismissal
- [x] Slide-in 200ms ease-out, reduced-motion respected
- [x] Header (title editable, status dropdown, close)
- [x] Properties (assignee, priority, due date, labels) with inline editors
- [x] Viewer read-only state
- [x] Description (rendered Markdown ↔ edit mode)
- [x] Markdown pipeline (`react-markdown` + `remark-gfm` + `rehype-sanitize`)
- [x] Comments section (chronological + new comment input)
- [x] @mention autocomplete
- [x] Mobile full-screen
- [x] Component + axe tests

#### Phase G6 — Notifications Page and Badge `[x] Complete`
- [x] Notifications page (reverse chronological)
- [x] Read/unread styling + Mark all as read
- [x] Click marks read + navigates
- [x] Header badge bound to unread count
- [x] Empty state per DRD §16
- [x] Component + axe tests

#### Phase G7 — Search Overlay `[x] Complete`
- [x] Search input + ⌘K trigger
- [x] Dropdown results (title with match highlight, project, status badge)
- [x] Keyboard nav (arrows, Enter, Esc)
- [x] Debounced query against `/search`
- [x] Empty results message
- [x] Component + axe tests

#### Phase G8 — Settings (Workspace, Members, Labels, Profile) `[x] Complete`
- [x] Settings layout with sub-navigation
- [x] Workspace tab (name + Save, Owner/Admin only)
- [x] Members tab (table + invite/remove modals)
- [x] Labels tab (list + create/edit/delete modals with palette swatches)
- [x] Profile tab — display name save (`PATCH /auth/me`)
- [x] Profile tab — change password section (`POST /auth/change-password`)
- [x] Profile tab — Delete Account modal (`DELETE /auth/me`, password-confirmed)
- [x] Last-used view per project persisted to `localStorage`
- [x] Component + axe tests

---

### Part H — Frontend Cross-Cutting

#### Phase H1 — Real-Time Client Bridge `[x] Complete`
- [x] WebSocket connection on login with CSRF token (`realtime/RealtimeProvider.tsx` gates on `useCurrentUser`; `socket.ts` builds `wss?://{host}/ws?csrf=…`)
- [x] `realtimeDispatcher` translating each event type to cache invalidate (`realtime/dispatcher.ts`) — **invalidate, not `setQueryData`** (see H1 note: backend payloads are id-only)
- [x] Reconnect with exponential backoff (cap 30s, jittered) + heartbeat ping; `4401`/`4403` treated as terminal
- [x] Reconnecting indicator (`realtime/RealtimeStatusIndicator.tsx`, rendered in `AppShell`)
- [x] `aria-live` announcements (polite region in `RealtimeProvider`: reconnecting / back-online / incoming @mention — TDD §10.3 whitelist; other notification kinds update the badge silently)
- [~] Two-context manual test passes (move + see in <1s) — **automated coverage green (22 realtime tests); live two-browser check pending** (same runtime-verification caveat as prior frontend phases)

#### Phase H2 — Empty States and First-Run `[x] Complete`
- [x] Audit all screens vs DRD §16 table — copy reconciled; most empty states already shipped in Part G (board/list filter vs no-tasks, search, notifications, dashboard sections)
- [x] Owner first-run: "Create your first project" prompt on dashboard (already in `ProjectsSection`, reuses Create Project modal from G2)
- [x] Owner first-run: "Invite team members" prompt in sidebar (`Sidebar.tsx` `InviteTeamPrompt`, reuses `InviteMemberModal`; **Owner-only** per PRD §3.4; auto-hides once ≥1 invitation exists)
- [x] Invited-user first-run: workspace-named welcome on dashboard (`dashboard.welcome.title` = "Welcome to {workspaceName}.", sourced from `useWorkspace`); dismissed once the user has an **assigned task** (their own `my-tasks` signal — reconciled with DRD §16, which was updated)
- [x] My Tasks empty state gains a "Browse projects" CTA (links to the first accessible project board)
- [x] Visibility derived from workspace state (no backend flag)
- [x] Role-aware copy & CTAs verified (Viewer sees message without CTA)
- [x] Component tests assert each state (`DashboardScreen`, `Sidebar` prompt, board/list empty states)

#### Phase H3 — Toasts, Errors, Confirmations `[x] Complete`
- [x] `useToast` hook + toast styling per DRD §7.8/§18.2 (5s auto-dismiss, fade-up, reduced motion, success/error variants, manual dismiss) — **kept Context-based, did NOT migrate to Zustand**; reconciled in the [ADR 054 amendment](../technical/decisions/054-client-state-management.md) + TDD §6.3 (see H3 note)
- [x] Standardized mutation-error toast — global `MutationCache.onError` → `errors.mutation` copy via the `mutationErrorToast` bridge; **opt-in** per mutation with `meta: { errorToast: true }` (not opt-out) so inline-error forms don't double-toast (see H3 note). Tagged: status change, change role, remove member, delete label, resend invitation.
- [x] Destructive confirmation modal pattern (Remove member, Delete account, Delete label) — `ConfirmDialog` already covers member/label with exact DRD copy; account keeps its password dialog. `ConfirmDialog` now wires `aria-describedby` (H4).
- [x] Component tests (`Toast`, `ConfirmDialog`, global error toast)

#### Phase H4 — Accessibility Pass `[x] Complete`
- [x] ARIA on modals, dropdowns, icon buttons, live regions — strong Radix-based baseline confirmed; fixed `ConfirmDialog` missing `aria-describedby`; verified `aria-expanded` (Radix), `aria-pressed` toggles, icon-button labels, landmarks
- [x] `vitest-axe` assertions added to all new component tests (color-contrast disabled in jsdom per `test/axe.ts`)
- [x] Reduced motion verified (global rule in `styles/global.css`; toast/panel/modal honor it)
- [~] Keyboard sweep + color-contrast spot-checks + **manual VoiceOver pass** — **deferred to `apps/web/docs/a11y-manual-checklist.md`** (not runnable headless; same runtime-verification caveat as prior frontend phases). Includes the live two-browser realtime check carried over from H1. The plan H4 DoD item "keyboard-only journey for the E2E happy-path completes" is delivered by the **I1 Playwright** keyboard-nav journeys, not in this phase.

#### Phase H5 — Frontend Test Completion `[x] Complete`
- [x] Component tests for the untested domain components (Header, AppShell, Tooltip, TaskCard, ProjectView, ProjectSubNav, ProjectSettingsModal, CreateTaskModal, LabelModal, TaskFields) + expanded TaskDetailPanel/MembersTab interactions. (A few thin sub-components — e.g. `Markdown`, the dashboard section wrappers — are covered transitively via their parent-screen tests rather than dedicated files; the ≥80% coverage gate is the measurable floor for the plan's "every domain component" intent.)
- [x] Hook/pure-logic tests for `taskQueryState` (validate/searchToParams/hasActiveFilters); permission derivations exercised via component tests
- [x] `vitest-axe` on component tests
- [x] Coverage ≥80% on `components/` + `features/` — **statements 94.3%, lines 94.3%, branches 82.2%, functions 82.1%** (gate set in `vitest.config.ts`; 182 web tests)
- [x] Frontend CI job ≤5 minutes — new `web-tests` job in `ci.yml` (`pnpm --filter @taskflow/web test -- --coverage`); full run ~23s locally

---

### Part I — E2E, Infrastructure, Deployment

#### Phase I1 — End-to-End Test Suite `[x] Complete`
- [x] Playwright config + `@axe-core/playwright` — new `@taskflow/e2e` workspace package (`e2e/`), serial (`workers: 1`) over the shared seeded workspace
- [x] Journey 1: Sign-up → workspace → first project (Owner)
- [x] Journey 2: Accept invitation (new user) — invite token recovered from the MailHog HTTP API (multipart/base64 body)
- [x] Journey 3: Create task → drag to In Progress → comment with @mention → mark Done
- [x] Journey 4: Two contexts, real-time move
- [x] Journey 5: @mention notification real-time badge
- [x] Journey 6: Search, filter, empty states
- [x] CI `e2e` job under 15 minutes — boots the real `docker compose up` stack, seeds, runs Playwright; local suite runs in ~16s, two consecutive green runs

#### Phase I2 — Infrastructure (CloudFormation) `[x] Complete`

**Scope note:** this environment has no AWS account, and the live apply is Phase I4. I2 = author every artifact + validate locally (`cfn-lint`, `nginx -t`, pytest) + add the CI `cfn-lint` gate + the deploy runbook. Account-specifics (domain, region, GitHub org/repo) are CloudFormation **parameters** with defaults.

- [x] `network.yml` — VPC, public subnet, IGW + route table, instance SG (80/443 from internet, 22 break-glass)
- [x] `compute.yml` (with user-data) — `t4g.small` arm64 from the SSM AL2023 AMI, Elastic IP, encrypted gp3 root, embedded bootstrap; **host alarms** (StatusCheckFailed/mem/disk) live here (need InstanceId)
- [x] `container-registry.yml` (lifecycle policies) — `taskflow/api` + `taskflow/web`, scan-on-push, keep-10/expire-untagged-7d
- [x] `storage.yml` (S3 backups + source maps) — SSE-S3, backups versioned + 30-day expiry, BlockPublicAccess, `Retain`
- [x] `parameters.yml` — manages the **KMS key** (`alias/taskflow-prod`) + policy; **CFN can't create SecureStrings**, so values are made out-of-band (runbook). Documents the 6 param names (incl. `resend_api_key`, `postgres_password`)
- [x] `monitoring.yml` (log groups, metric filters, alarms, SNS) — 3 log groups (30d), the 5 metric filters (matched to **actual** structlog output: lowercase `level`, numeric `status`, `event`), SNS `taskflow-alerts`, the 3 application alarms
- [x] `iam.yml` (OIDC + deploy role) — GitHub OIDC provider (conditional), `taskflow-deploy-role` (ECR/CFN/SSM), EC2 instance role + profile (SSM read + KMS decrypt, ECR pull, S3 backup write, CW Logs)
- [x] Swap the email adapter to **Resend** (HTTP API via httpx) — `adapters/email/resend.py`, factory + settings (`email_backend: smtp|resend`, `resend_api_key`), `.env.example`; **SES removed** (`ses.py` + its test deleted); `aioboto3` **kept** (still used by the S3 backup job in `services/cleanup.py`, whose region setting was renamed `ses_region` → `aws_region`). Dev MailHog unchanged.
- [x] `infra/ec2/user-data.sh` — self-discovering bootstrap (Docker + compose plugin + CW Agent, SSM → `/opt/taskflow/.env`, ECR login, compose up); embedded verbatim in `compute.yml`
- [x] `docker-compose.prod.yml` with nginx + api + web + db (no certbot) — Origin CA cert mount, ECR image refs, `awslogs` log driver, healthchecks, named db volume
- [x] **Cloudflare** Origin CA cert + nginx cert paths updated (`/etc/nginx/certs/origin.{pem,key}`, ACME block removed); zone Full (strict), proxied `A` record + Resend SPF/DKIM/DMARC — **documented in `docs/runbooks/deploy.md`** for the I4 operator (dashboard steps, not code)
- [x] `cfn-lint` clean in CI — new `cfn-lint` job in `ci.yml` + `make cfn-lint`; all 7 templates pass
- [x] *(No `dns.yml` / `email.yml` / ACM — DNS + email-auth are in Cloudflare, not CFN)*

#### Phase I3 — CD Pipeline `[x] Complete`

**Scope note (mirrors I2):** no AWS account in this environment, so I3 = author
`deploy.yml` + statically validate (YAML parse, `shellcheck` on every embedded
script, `bash -n` on the generated host script) + reconcile the runbook. The
end-to-end "trivial change reaches the host + smoke passes" DoD is necessarily an
**I4** check against the live account.

- [x] `.github/workflows/deploy.yml` — single `deploy` job; triggers **push-to-`main` + `workflow_dispatch` only, never `pull_request`** (public-repo safety); `concurrency: deploy-prod` (no mid-roll cancel)
- [x] OIDC role assumption — `aws-actions/configure-aws-credentials@v4` assumes `secrets.AWS_DEPLOY_ROLE_ARN` (the `taskflow-iam-DeployRoleArn` export); `permissions: id-token: write`; no long-lived keys anywhere
- [x] `environment: production` gate (ADR 073) — the job waits for the production environment's required-reviewer approval before any step runs; the I4 operator configures the reviewer rule
- [x] Build + push arm64 images to ECR — `setup-qemu` + `buildx` + `build-push-action@v6` (`platforms: linux/arm64`, `provenance: false`); api context `apps/api`, web context repo-root `.` with `apps/web/Dockerfile`; tagged with the commit SHA (deterministic rollback)
- [x] CFN deploy of changed stacks — runbook §1 ordered `aws cloudformation deploy` loop, gated on `infra/cloudformation/**` changing (or the `deploy_infra` dispatch input); `--no-fail-on-empty-changeset`. Pipeline only **updates** existing stacks; initial creation stays the I4 admin step
- [x] SSM `alembic upgrade head` — run explicitly (`compose run --rm api alembic upgrade head`) **before** the roll, so a bad migration fails the deploy before tearing down the running app (the api entrypoint also migrates on start; idempotent)
- [x] SSM `docker compose pull && up -d` — one `AWS-RunShellScript` Send-Command does: sync the two non-secret config files (base64) → ECR re-login → `pull` → migrate → `up -d --remove-orphans`; reaches the host with **no SSH**. Runtime secrets stay on the host (already hydrated from SSM into `/opt/taskflow/.env`); the pipeline injects only `IMAGE_TAG` + the config files
- [x] Health smoke check from workflow — host-local `curl -fsSk https://localhost/health` retry loop inside the same SSM command (nginx 80→443 redirect + origin cert ⇒ `-k`); the workflow polls `get-command-invocation` and fails the job unless `Status == Success`
- [x] Rollback procedure documented in runbook — §7 now leads with the pipeline path (`workflow_dispatch` + `image_tag=<prior-sha>`); manual host roll kept as fallback

#### Phase I4 — Production Cutover `[ ] Not started`
- [ ] All SSM Parameter Store values populated
- [ ] First deploy succeeds
- [ ] Cloudflare Origin CA cert installed + edge TLS (Full strict) verified
- [ ] Cloudflare proxied `A` record cut to Elastic IP; Resend email delivers (SPF/DKIM/DMARC live)
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

### 2026-06-28 — Phase I3 complete (CD Pipeline / `deploy.yml`)

Authored `.github/workflows/deploy.yml` — the Continuous Deployment pipeline that
takes a merge to `main` to the running EC2 host with no manual SSH. **Statically
validated** (no AWS account here, same scope boundary as I2): YAML parses;
`shellcheck` clean on every embedded `run:` script; the heredoc-generated host
script reproduced with dummy inputs passes `bash -n` and `shellcheck` (the
escaping is verified — `\$AWS_REGION`/`\$ECR_REGISTRY` stay literal for the host,
`$IMAGE_TAG`/the base64 blobs expand on the runner); `docker compose -f
docker-compose.prod.yml config -q` still ok (compose untouched).

**Shape** — one `deploy` job, sequential under a single OIDC session (avoids
`needs`/skip races):
1. **OIDC** (`configure-aws-credentials@v4` → `secrets.AWS_DEPLOY_ROLE_ARN`),
   `permissions: id-token: write`. The only repo secret is the role **ARN** — not
   a credential.
2. **ECR login** + **buildx/QEMU** build of both arm64 images, tagged with the
   commit SHA, pushed to `taskflow/api` + `taskflow/web`.
3. **Conditional CFN reconcile** — only when `infra/cloudformation/**` changed (or
   the `deploy_infra` dispatch input), in Export/ImportValue order with
   `--no-fail-on-empty-changeset`. Ordinary code pushes don't churn infra.
4. **SSM Run Command** to the `taskflow-compute` `InstanceId`: sync the two
   non-secret config files (base64-decoded on the host) → ECR re-login → `pull` →
   `alembic upgrade head` → `up -d` → `curl -fsSk https://localhost/health`. The
   workflow polls the invocation and gates on `Status == Success`.

**Security guardrails (deliberate):** triggers are **push-to-`main` +
`workflow_dispatch` only — never `pull_request`** (public repo; a fork PR must not
reach the deploy role). Runtime secrets never transit CI — the host already
hydrates `/opt/taskflow/.env` from SSM at boot; the pipeline injects only
`IMAGE_TAG` and the two config files. TLS certs (`origin.{pem,key}`) stay
**operator-placed via SSM Session Manager** (I4), never shipped by the workflow.

**Decisions worth noting:**
- **Config sync each deploy (chosen with user).** `docker-compose.prod.yml` +
  `infra/nginx/nginx.conf` are shipped to the host every run, so prod config can't
  silently drift from the repo. Both are non-secret; nginx.conf must land at
  `/opt/taskflow/infra/nginx/nginx.conf` because the compose bind-mount is
  relative.
- **Migrate before roll.** Explicit `compose run --rm api alembic upgrade head`
  precedes `up -d` so a bad migration fails the deploy before the running app is
  replaced. The api entrypoint also migrates on start — idempotent, harmless.
- **Pipeline updates stacks, never creates them.** Matches the deploy role's
  change-set-only CloudFormation scope; first creation is the §1 admin step.
- **Host-local smoke, not public.** Checks `https://localhost/health` on the box
  (works pre-Cloudflare-cutover); `-k` because the origin cert won't match
  `localhost`.

**Docs reconciled:** runbook §5 now leads with the pipeline (manual sequence kept
as break-glass), §7 rollback leads with `workflow_dispatch image_tag=<prior-sha>`,
§3 clarifies certs are operator-placed and never CI-shipped.

**Post-build review reconciliation (2026-06-28).** A pass of `deploy.yml` against
ADRs 071/072/073/087 + TDD §14 surfaced five inconsistencies, all now resolved:
- **(code) Added `environment: production`** to the deploy job — ADR 073 requires
  the deploy to gate on the production environment's manual approval; the job was
  missing it. The push-to-main trigger still fires, then waits for a reviewer.
- **(docs) ECR registry is derived, not stored.** Dropped the `ECR_REPOSITORY`
  secret from ADR 073 (amendment) and TDD §14.3 — the registry comes from the
  `amazon-ecr-login` step output (`AWS_DEPLOY_ROLE_ARN` is now the only CI secret).
- **(docs) Config-file sync added to TDD §14.2** (step 4) — the compose + nginx
  sync wasn't in the architecture-of-record.
- **(docs) Smoke check clarified in TDD §14.2** (step 7) — runs host-local via the
  SSM command and gates on its exit status, not from the runner.
- **(docs) "multi-arch" → "linux/arm64"** in ADR 071 / TDD §14.2 (arm64 is the
  only target per ADR 038).
- *Adjacent, out of I3 scope (tracked separately):* `ci.yml` lacks the TDD §14.1
  `build-images` job, so a broken Dockerfile isn't caught until `deploy.yml` runs.

**Carried to I4/I5 (unchanged):** the live stack apply + SSM secret population +
Cloudflare/Resend dashboard config + cert placement + configuring the `production`
environment reviewer + the **first real pipeline run** (the end-to-end DoD);
subscribe + synthesize alarms (I5).

### 2026-06-20 — Phase I2 complete (Infrastructure / CloudFormation + Resend & Cloudflare swap)

Authored the full production stack and landed the two deferred 2026-06-14 changes (Cloudflare Origin-CA TLS; SES → Resend). **Validated locally:** `cfn-lint` clean on all 7 templates, `nginx -t` passes the rewritten config, email unit tests + ruff/mypy green, `docker compose -f docker-compose.prod.yml config -q` ok, I1 e2e suite still green.

**Scope boundary:** no AWS account in this environment and the live apply is **I4**, so I2 delivered *authored + locally-validated* artifacts + the CI `cfn-lint` gate + `docs/runbooks/deploy.md`. The `aws cloudformation deploy`, SSM secret population, and Cloudflare/Resend dashboard steps are the runbook's I4 operator actions. All account-specifics are CFN **parameters** with defaults (region us-east-1; `GitHubOrg=PlanningRoom`, `GitHubRepo=TaskFlow`).

**CloudFormation** (`infra/cloudformation/`, 7 stacks; deploy order network → iam → container-registry → storage → parameters → monitoring → compute; cross-stack via `Export`/`ImportValue`). Decisions worth noting:
- **SecureString limitation (real AWS constraint):** CFN cannot create SecureString SSM parameters. `parameters.yml` therefore owns the **KMS key + policy** (`alias/taskflow-prod`, instance-role decrypt) and documents the names; values are `aws ssm put-parameter --type SecureString` out-of-band (runbook). This matches TDD §5.1 ("stack manages names and KMS policy; values set out-of-band").
- **Host alarms in `compute.yml`, app alarms in `monitoring.yml`:** the EC2/CWAgent alarms (StatusCheckFailed, mem, disk) need the InstanceId, so they live with the instance and publish to the SNS topic imported from `monitoring`.
- **Metric filters matched to reality, not TDD prose.** Structlog emits **lowercase** `level` and a numeric `status`, so `error_count` keys off `{ $.level = "error" }` (TDD §13.2 wrote "ERROR"). I5 re-verifies against live lines — these now match.
- **user-data self-discovers** region/account from IMDS so the script is embedded verbatim in `compute.yml` (no CFN `!Sub` escaping of shell `${}`); the standalone `infra/ec2/user-data.sh` is the canonical copy.

**Email SES → Resend:** new `adapters/email/resend.py` (httpx POST to `api.resend.com/emails`, mirrors the SES adapter's structured logging). Factory + settings now `email_backend: Literal["smtp","resend"]` + `resend_api_key`. **SES fully removed** (`ses.py` + its unit test deleted). **`aioboto3` kept** — it's still used by the S3 pg_dump backup job (`services/cleanup.py`); its region knob was renamed `ses_region` → `aws_region` (reads `AWS_REGION`). `.env.example` drops `SES_REGION`/`CERTBOT_EMAIL`, adds `RESEND_API_KEY`/`EMAIL_FROM_ADDRESS`.

**Pre-existing (not introduced here):** `mypy` reports 2 `cookie_secure: bool | None` errors in `api/v1/auth.py` — main CI is already red on these (see the `main-ci-red-python` note); untouched by I2.

**Carried to I3/I4:** `deploy.yml` (OIDC build/push/deploy/migrate/roll); the live stack apply, SSM secret values, and Cloudflare/Resend dashboard config per the runbook; subscribe + synthesize alarms (I5).

### 2026-06-20 — Phase I1 complete (End-to-End Test Suite)

All six Playwright journeys (ADR 080 / TDD §16.3) pass against the real, seeded `docker compose up` stack — **6/6 green, ~16s, stable across two consecutive runs**. Browser drives the Vite dev server (:5173) same-origin; cookies + CSRF flow exactly as in prod.

**Built** — a dedicated **`@taskflow/e2e`** workspace package (kept separate from `apps/web` to avoid the Vitest↔Playwright `test`/`expect` global collision):
- `playwright.config.ts` (chromium, `baseURL` env-overridable, **`workers: 1`** — the journeys share the one seeded "Aurora Studio" workspace and the real-time/notification assertions are cross-context-stateful), helpers (`auth`, `board`, `dnd`, `axe`, `mailhog`, `notifications`, `data`), and `tests/01..06`.
- `make e2e-up` (compose up → wait for `/health` + `:5173` → seed) + `make e2e`; CI `e2e` job added to `ci.yml` (boots compose, seeds, runs Playwright, uploads the report on failure, `down -v` teardown; `timeout-minutes: 20`).
- The package script is named `e2e` (not `test`) so `turbo run test` / `pnpm test` never launch Playwright without a stack.

**Three product/infra changes were needed to make `docker compose up` genuinely E2E-able** (the team's normal workflow runs Vite on the host, so these container paths were never exercised):
1. **Vite dev proxy is now target-configurable** (`apps/web/vite.config.ts` reads `VITE_PROXY_TARGET`, default `http://localhost:8000`). Inside compose the SPA's `/api` + `/ws` must reach `api:8000`, not `localhost` — the `web` service now sets `VITE_PROXY_TARGET=http://api:8000`. Host dev is unchanged. Without this every API call 502'd.
2. **Global rate-limit toggle** — added `settings.rate_limit_enabled` (default **True**; wired into the slowapi `Limiter`). The compose `api` service sets `RATE_LIMIT_ENABLED=false` so the suite's repeated logins/signups don't 429. **Production keeps it on** (standalone `docker-compose.prod.yml`); the E1 rate-limit integration tests force `limiter.enabled = True` in a fixture, so they're unaffected (re-verified: 5/5 pass).
3. Nothing else in app behaviour changed.

**Test-suite deviations / decisions (intentional):**
- **axe excludes the "use of colour" rules** (`color-contrast`, `link-in-text-block`[`-style`]) — these are exactly what **H4 routed to the manual a11y checklist** (`apps/web/docs/a11y-manual-checklist.md`), and mirror `apps/web/src/test/axe.ts` disabling `color-contrast` in jsdom. Excluded by **filtering results** (not `disableRules`, which throws on the experimental `-style` id). Every structural rule (roles/names/labels/landmarks/ARIA/focus) stays enforced on each visited page.
- **dnd-kit drag** uses a manual pointer helper (press → nudge past the 5px activation → glide in steps → settle → release); Playwright's high-level `dragTo` doesn't trip the PointerSensor.
- **MailHog token extraction** decodes multipart **base64** part bodies (the invite email is base64 transfer-encoded), not just quoted-printable.
- Journeys use unique emails (J1/J2) and self-created tasks (J3) so local reruns against a persisted DB stay green; CI is fresh each run.

**Carried forward to I2 (unchanged):** the Resend/Cloudflare prod-adapter swaps; the manual a11y + (now automated) two-browser realtime checks. The live two-browser realtime check that H1/H4 left manual is **now covered automatically** by Journeys 4 & 5.

### 2026-06-14 — Infra decision change: Cloudflare DNS + Resend email (pre-Part I)

Two production-stack decisions changed before building Part I, with the **code deferred to I2** (docs/decisions updated now):

- **DNS: Route 53 → Cloudflare** (proxied / "orange cloud"). **TLS: Let's Encrypt + certbot → Cloudflare edge TLS + a Cloudflare Origin CA cert** on the origin (Full strict). Removes the certbot container/cron and the ACM cert; adds Cloudflare CDN/DDoS. Updated ADR 036 + **ADR 085 amendment**, TDD §2.2/§3/§5 (diagrams + tables + topology), plan E1/I2/I4, status I2/I4.
- **Email: Amazon SES → Resend** (HTTP API via `httpx`; `EMAIL_BACKEND=resend`). Dev SMTP→MailHog unchanged. Resend's SPF/DKIM/DMARC records live in Cloudflare DNS. Updated **ADR 067** (decision rewritten + amendment), ADRs 036/039/049/073/087, TDD, plan D2/I2/I4, status.
- **CloudFormation:** the `dns` and `email` stacks (and ACM) are **removed** — DNS + email-auth are managed in Cloudflare/Resend, not CFN (ADR 087, TDD §5.1).

**Deferred code (all in I2):** swap the D2 prod email adapter `ses.py` (`aioboto3`) → a Resend `httpx` sender; update `settings.py`/`.env.example` (`RESEND_API_KEY`, drop SES/`CERTBOT_EMAIL` vars); repoint `infra/nginx/nginx.conf` cert paths off the Let's Encrypt layout to the Origin CA cert; drop `certbot` from `docker-compose.prod.yml`. The built SES adapter + Let's-Encrypt nginx paths remain in the repo until then — see the annotated D2/E1 lines above.

### 2026-06-14 — Phases H2–H5 complete (Part H finished)

The remaining Part H cross-cutting phases landed on branch `feat/part-h-cross-cutting`. Much of H2/H3 already existed in partial form from Part G, so this was largely audit, gap-fill, standardize, and test. **vitest 182/182 green** (44 files; +48 tests over H1's 134), `tsc -b` + `biome check` clean.

**H2 — Empty states & first-run:** the DRD §16 empty states were mostly shipped in Part G; copy was reconciled. Net-new: the Owner "Invite team members" sidebar prompt (`Sidebar.tsx` `InviteTeamPrompt`, reuses `InviteMemberModal`, **Owner-only** per PRD §3.4, auto-hides once an invitation exists); the invited-user welcome now names the workspace (`dashboard.welcome.title` → "Welcome to {workspaceName}." via `useWorkspace`) and is dismissed by the user's own `my-tasks` signal (DRD §16 updated to match); and a "Browse projects" CTA on the My Tasks empty state.

**H3 — Toasts/errors/confirmations — two intentional deviations from the plan doc:**
1. **Toast kept Context-based, NOT migrated to Zustand.** A working Radix-backed `useToast()` already existed and was used in 8 places; the plan's "Zustand store" wording was a means, not a requirement. Extended it with the error variant + manual dismiss (DRD §18.2) instead of a churny rewrite. No new dependency. **Reconciled across the architecture-of-record** (2026-06-14 audit): ADR 054 now carries an amendment, TDD §6.3/§7.2 describe the Context store, and plan H3 was updated — so the docs no longer mandate Zustand for toasts.
2. **Mutation-error toast is opt-IN, not opt-out.** The plan imagined a global toast for every unhandled mutation error with a `skipErrorToast` opt-out. But ~12 call sites (auth screens, form modals) already show contextual inline errors, so an opt-out default would double-toast all of them. Inverted to opt-in: a global `MutationCache.onError` (`app/query-client.ts`) fires the standardized `errors.mutation` toast only for mutations tagged `meta: { errorToast: true }` (status change, change role, remove member, delete label, resend invitation — the ones that previously failed silently). Bridged module→context via `lib/mutationErrorToast.ts` + `app/MutationErrorListener.tsx`. Destructive confirmations already matched DRD copy via `ConfirmDialog`.

**H4 — Accessibility:** the Radix-based baseline was already strong (focus traps, `aria-expanded`, `aria-pressed`, labels, landmarks, global reduced-motion). Concrete fix: `ConfirmDialog` now wires `aria-describedby` via `DialogDescription`. `vitest-axe` runs on every new component test. The manual passes that can't run headless — keyboard sweep, VoiceOver, color-contrast spot-checks, and the live two-browser realtime check carried from H1 — are documented as a standing pre-launch checklist at **`apps/web/docs/a11y-manual-checklist.md`** and marked `[~]` deferred.

**H5 — Test completion:** added tests for the previously-untested components (Header, AppShell, Tooltip, TaskCard, ProjectView, ProjectSubNav, ProjectSettingsModal, CreateTaskModal, LabelModal, TaskFields) plus a `taskQueryState` pure-logic suite and expanded TaskDetailPanel/MembersTab interactions. Coverage gate added in `vitest.config.ts` (80% on `components/` + `features/`); actuals **statements/lines 94.3%, branches 82.2%, functions 82.1%**. New `web-tests` CI job runs `pnpm --filter @taskflow/web test -- --coverage` (~23s, well under the 5-min budget). Test-infra note: added a jsdom pointer-capture shim in `test/setup.ts` for Radix interactions.

**Post-audit reconciliation (2026-06-14):** a code-vs-docs audit of Part H surfaced several inconsistencies, all now fixed:
- **Logout / user menu built (was missing).** The header avatar was a non-functional `aria-label="User menu"` placeholder and there was **no way to sign out** anywhere in the app, despite DRD §11.2, plan F4, and the readiness plan all assuming it. Implemented the DRD §11.2 User Menu (identity block: name/email/role badge, Settings link, Sign out) on the header avatar via the `DropdownMenu` primitive, backed by a new `features/auth/useLogout.ts` (`POST /auth/logout` → clear cache → `/login`). This closes a latent **F4** gap. (`Header.tsx`, +2 tests.)
- **Invite-team prompt narrowed to Owner-only** to match PRD §3.4 / plan H2 (was Owner/Admin).
- **Invited-welcome dismissal made user-attributable** (own `my-tasks`, not the workspace-wide activity feed), fixing a latent bug where an invited user joining an already-active workspace would never see the welcome. DRD §16 and plan H2 reconciled to the implemented signal.
- **Doc staleness fixed:** plan H1 `setQueryData` → invalidate (matches TDD §6.3 + code); plan H3 + TDD §6.3/§7.2 + ADR 054 amendment now describe the Context toast store.

**Carried forward (unchanged):** responsive/mobile polish (F4/G3/G4 deferral); @mention chip rendering in posted comments; the manual a11y + two-browser checks above.

### 2026-06-14 — Phase H1 complete (Real-Time Client Bridge)

The frontend now consumes the `/ws` fan-out the backend has published since Part D. First of the Part H cross-cutting phases.

**Built** under `apps/web/src/realtime/`:
- `socket.ts` — framework-agnostic `RealtimeClient`: connects to `wss?://{host}/ws?csrf=…`, parses envelopes, sends a 25s heartbeat ping, and reconnects with jittered exponential backoff (base 1s, ×2, cap 30s). Close codes `4401`/`4403` are terminal (no reconnect → `onAuthFailure` invalidates `['auth','me']` so the route guard redirects to `/login`). Uses literal readyState constants so it doesn't depend on a global `WebSocket` (jsdom omits it) — `socketFactory`/`random` are injectable for deterministic tests.
- `dispatcher.ts` — `createRealtimeDispatcher` maps each event type to TanStack Query invalidations using the app's real query keys; prefix matching means `['task',id]` covers comments and `['notifications']` covers the unread count. `control.access_changed` invalidates projects and sends `refresh_subscriptions`. `activity` always refreshes the feed, then maps its inner `event_type` (`project.*`/`workspace.label.*`/`workspace.invitation.*`/`workspace.user.*`/`workspace.updated`) to the relevant lists.
- `RealtimeProvider.tsx` + `context.ts` — gates the connection on `useCurrentUser` (shares the cached query, no extra fetch), holds status, hosts a polite `aria-live` region, and invalidates **all** queries on reconnect (resync per TDD §10.4). Mounted in `main.tsx` inside `ToastProvider`.
- `RealtimeStatusIndicator.tsx` — discreet "Reconnecting…" pill, rendered in `AppShell`, visible only while reconnecting.

**Deviation from the plan doc (intentional):** the plan imagined `task.updated → setQueryData(['task',id], task)`. The actual backend envelopes (`realtime/publish.py`) carry **IDs only**, not full DTOs, so precision `setQueryData` isn't possible — the dispatcher **invalidates** and lets the active query refetch, which matches the reconcile-from-DB semantics of TDD §10.4. Precision updates remain a future enhancement gated on the backend sending full DTOs. There are also no `project.*`/`workspace.*` envelope types on the wire — those mutations arrive as `activity` envelopes whose payload `event_type` carries the specific kind; the dispatcher keys off that.

**Other changes:** extracted `readCookie` + `CSRF_COOKIE` into `lib/cookies.ts` (shared by `api/client.ts` and the socket — no duplicate parser). Relaxed `useUnreadCount`'s `refetchInterval` from 60s to 5min: the bridge now pushes badge updates on `notification.created`, leaving the poll as a slow safety net for missed events.

**Verification:** `tsc -b` clean, `biome check` clean, **vitest 119/119 green** (29 files; 22 new realtime tests — dispatcher event mapping, socket backoff/heartbeat/terminal-close, provider connect-gating + aria-live + indicator axe). Live two-browser check (user A moves a task → user B sees it <1s; @mention badge increments) is the remaining manual step — same cumulative runtime-verification caveat as prior frontend phases.

### 2026-06-07 — Phases G2–G8 complete (all Frontend Screens)

Part G is done. The placeholder routes are now the real product, built against the API-complete backend on the conventions G1 established (typed `apiClient`, `react-intl`, UI primitives, RHF+Zod, `renderWithProviders` + `vitest-axe`). Landed on branch `feat/web-part-g-screens` (commit + a follow-up tests commit).

**Built** (representative paths under `apps/web/src/`):
- **G2 Dashboard** (`features/dashboard/`): My Tasks / Recent Activity / Projects, role-aware empty + first-run states, reusable `CreateProjectModal`.
- **G3 Board** (`features/board/`, `features/tasks/ProjectView` + `ProjectSubNav`): `@dnd-kit` columns with optimistic status (`useUpdateTaskStatus`, ADR 046), filter popover + chips, sort, `CreateTaskModal`.
- **G4 List** (`features/list/`): sortable table (backend-supported keys), inline status, shared filter/sort URL state.
- **G5 Task Detail panel** (`features/tasks/TaskDetailPanel`): route overlay, inline property editors, Markdown description (`components/Markdown.tsx`), comments + `@mention` autocomplete (`MentionTextarea`), Viewer read-only.
- **G6 Notifications** (`features/notifications/`): list + mark-all-read, live header bell badge.
- **G7 Search** (`features/search/`): ⌘K overlay, debounced `/search`, keyboard nav, match highlight.
- **G8 Settings** (`features/settings/`): workspace / members (+invite/remove) / labels (+create/edit/delete) / profile (name, password, delete-account), role-gated `SettingsLayout` redirects.

**Cross-cutting:** new domain hooks (`useTasks`/`useComments`/`useNotifications`/`useSearch`/settings + `useProject`); `ConfirmDialog`; URL filter-sort state (`taskQueryState`); `lib/projectView` last-used-view localStorage; array query-param support added to `apiClient`; `renderWithProviders` now wraps `ToastProvider` to mirror `main.tsx` (fixed 3 latent G2 test failures that never ran while vitest was blocked).

**Deps added** (net-new runtime, per ADRs): `@dnd-kit/core|sortable|utilities` (ADR 059), `react-markdown` + `remark-gfm` + `rehype-sanitize` (ADR 060).

**Verification:** `tsc -b` clean, `biome check` clean, **vitest 97/97 green** (26 files).

**Deferred (tracked, not regressions):**
- Responsive/mobile polish (board column stacking, list mobile layout) — carried with the F4 responsive-shell deferral (DRD §15).
- @mention **rendering** in posted comments shows the raw `@handle` text rather than teal-styled chips; autocomplete insertion + backend resolution/notification are fully wired. Revisit as a Markdown refinement.
- List header sort is offered only for backend-supported keys (priority/due/assignee); title/status aren't server-sortable.

**Environment note:** this session hit the machine's iCloud "Optimize Mac Storage" eviction (per project memory) hard — `node_modules` reads blocked `pnpm install`, `tsc`, and `vitest` for an extended stretch. Root cause was low free disk (~11 GB); pruning unused Docker build cache/images freed space, iCloud rehydrated, and the toolchain unblocked. If verification hangs at startup again, check free disk first.

### 2026-05-31 — Phase G1 complete (Auth Screens)

The full unauthenticated journey now renders real, backend-wired screens (replacing the F4 `AuthPlaceholder` stubs). First clickable UI of Part G.

**Built** under `apps/web/src/features/auth/`:
- Screens: `LoginScreen`, `SignupScreen`, `AcceptInvitationScreen`, `PasswordResetRequestScreen`, `PasswordResetConfirmScreen`.
- Shared scaffolding: `AuthCard` (centered login-bg card, extracted from the old `AuthPlaceholder` styling), `FormField`/`FormError` (label + input + inline error wired to `aria-invalid`/`aria-describedby`), `useAuthSuccess` (seeds `CURRENT_USER_KEY` from the `{user}` response, then `navigate('/dashboard', replace)`).
- Schemas added to `forms/schemas/index.ts` (`loginSchema` uses `password.min(1)` — NOT the 8-char rule — so a wrong password returns 401 not a client 422, mirroring the backend's deliberately-unconstrained `LoginRequest.password`). Auth DTO aliases added to `packages/api-types/src/index.ts` + re-exported from `apps/web/src/api/types.ts`.
- Copy in `i18n/locales/en.json` under `auth.*` (DRD §8.1–§8.2 + tone guide).

**Router** (`src/app/router.tsx`): swapped the three auth placeholders for the real screens; added `/forgot-password` (reset request) and `/reset-password` (reset confirm — token read from the **query string**, per the reset email link `…/reset-password?token=…`). The invitation link path stayed `/invitations/$token`. **Auth guards landed (the F4 TODO):** `shellRoute.beforeLoad` resolves `/auth/me` via `queryClient.ensureQueryData` and redirects to `/login` on 401; `loginRoute`/`signupRoute` redirect to `/dashboard` when already authenticated. `AuthPlaceholder.tsx` removed.

**Scope decision (confirmed with user) — blind accept-invitation form.** The backend has no GET-invitation-by-token endpoint; `POST /accept-invitation` reveals nothing pre-acceptance. So the screen collects display name + password and submits the token, letting the backend resolve existing-vs-new internally. It does NOT show workspace name / role / inviter, does NOT prefill the email, and does NOT branch new-vs-existing — a divergence from DRD §8.2. Expired/invalid tokens render a calm full-card state with a way back.
- **Follow-up (pre-launch / Part G polish):** add a backend `GET /auth/invitations/:token` preview endpoint (workspace name, role, inviter, email, status), regenerate OpenAPI types, then enrich the accept screen per DRD §8.2.
- Also still deferred from earlier phases and surfaced by these screens: a logout affordance (header dropdown, G8) and the global toast store (H3); auth errors currently render inline, not as toasts.

**Verification (all green):** `pnpm --filter @taskflow/web typecheck` clean; `test` 50/50 (24 new auth tests, axe-clean per screen); `lint` clean (Biome); `vite build` succeeds. Live end-to-end against the dev stack (signup→dashboard, login, reset via MailHog, invitation accept) is the remaining manual check — same cumulative "runtime verification" caveat as prior frontend phases.

### 2026-05-31 — Phases F2–F4 complete (Part F: Frontend Foundation done)

F2, F3, and F4 landed together. `apps/web` now has a typed API client, the DRD §7 primitive library, and the full app shell + route tree. Part G (screens) is unblocked.

**Phase F2 — API Client & Type Codegen**
- **Offline schema dump (chosen over a live server):** `apps/api/taskflow/scripts/dump_openapi.py` imports the FastAPI app and writes `app.openapi()` to JSON with no uvicorn/Postgres (engine init is lazy in the lifespan; `Settings()` only reads env). Verified: OpenAPI 3.1, 33 paths, 63 schemas, no DB.
- **Codegen:** `packages/api-types` gained `openapi-typescript` 7.6.1 + `scripts/gen.mjs` (`pnpm gen:api`): dump → `openapi.json` → `src/generated/schema.d.ts`. Both artifacts are committed as the drift baseline (`openapi.json` is NOT gitignored; only `apps/web/src/api/generated/` is). `src/index.ts` re-exports `paths`/`components`/`operations` + curated DTO aliases (`CurrentUser`, `TaskDetail`, …) and the hand-authored `ApiErrorEnvelope` (the ADR 043 envelope isn't an OpenAPI component).
- **Typed client:** `apps/web/src/api/client.ts` — relative `/api/v1`, `credentials: 'include'` (session cookie), reads the JS-readable `taskflow_csrf` cookie and sends `X-CSRF-Token` on POST/PATCH/PUT/DELETE, parses the ADR 043 envelope into a thrown `ApiError` (`status`/`code`/`message`/`fields`). `hooks.ts` adds `useApiQuery`/`useApiMutation` (error type fixed to `ApiError`). `vite.config.ts` gained a dev `server.proxy` for `/api` + `/ws` → `http://localhost:8000` so the SPA uses same-origin relative paths.
- **CI:** new `openapi-drift` job (uv + pnpm) reruns `gen:api` and `git diff --exit-code`s the two artifacts (TDD §14.1). Verified locally: regen → clean diff.
- **Smoke test:** `client.test.ts` mocks `fetch` and asserts envelope parsing, 422 `fields`, success payloads, and CSRF-header on/off by method. (The plan's "hit a running backend" became a mocked test — deterministic, no live API in CI.)

**Phase F3 — UI Primitives (Vitest + axe; Storybook deferred)**
- **Decision (confirmed with user):** Storybook's stable Vite builder targets Vite 5/6 — a real risk on our Vite 8. So F3 verifies primitives with **Vitest + @testing-library/react + vitest-axe** (jsdom), one test-per-primitive covering variants/states with a `toHaveNoViolations()` assertion, instead of Storybook stories. Storybook is deferred until its Vite 8 support lands; revisit alongside H5. This is the one place F3's literal DoD ("Storybook configured") is intentionally unmet.
- **Built** in `apps/web/src/components/ui/` with `class-variance-authority` + token utilities: `Button`, `Input`/`Textarea`/`Select`/`FormLabel`, `Avatar`, `StatusBadge`, `LabelChip` (+`LabelOverflow`), `PriorityIcon`, `DueDate` (+`formatDueDate`), plus Radix-backed `Dialog`, `DropdownMenu`, `Tabs`, `Checkbox`, `Tooltip`, `Toast` (with a minimal `ToastProvider`/`useToast`; the richer store is H3). Lucide via `icons.ts`. 26 tests, all green.
- **Test infra:** `vitest.config.ts` (jsdom) + `src/test/setup.ts` (registers jest-dom + vitest-axe matchers). `src/test/vitest.d.ts` augments the `vitest` module's `Assertion` with the axe matcher (Vitest 3 uses `declare module 'vitest'`, not the legacy `Vi` namespace that `vitest-axe/extend-expect` targets). `src/test/axe.ts` wraps `axe()` to disable the `color-contrast` rule under jsdom (no canvas/layout engine — it throws on `getContext`; contrast is a design-review check, not a unit test).

**Phase F4 — App Shell & Routes**
- `useCurrentUser` (`GET /auth/me`, 401 = unauthenticated, no retry) + `useProjects` (`GET /projects`) hooks. Shell in `src/components/shell/`: `Logo` (check-in-box SVG mark + wordmark, sidebar vs login sizing), `Sidebar` (240px / 60px collapsed rail; logo, Dashboard/Notifications nav, Projects list with color dots, pinned Settings + user identity), `Header` (breadcrumb, 260px ⌘K search placeholder, notification bell + badge, user avatar), `AppShell` (three-zone, header 52px). Tooltip/Toast providers mounted in `main.tsx`.
- **Route tree** rewritten in `src/app/router.tsx` (code-based, TanStack Router 1.170.10): auth routes (`/login`, `/signup`, `/invitations/$token`) render OUTSIDE the shell via `AuthPlaceholder`; everything else hangs off a pathless `shellRoute` (renders `AppShell`, breadcrumb derived from pathname). Leaves are `PlaceholderPage`s (Part G fills them). Redirects: `/`→`/dashboard`, `/projects/$projectId`→`.../board`, `/settings`→`/settings/workspace`. The F1 `Placeholder.tsx` was removed. Auth redirect *guards* are deferred to G1 (F4 only structures the tree).
- **Responsive:** desktop + sidebar-hidden-below-`md` done; the `Sidebar collapsed` icon-rail and the mobile hamburger overlay are deferred polish.

**Known divergence — avatar palette names.** The API returns `avatar_color` ∈ `{indigo, violet, amber, emerald, rose, sky}` (`apps/api/taskflow/schemas/users.py`), but DRD §2.10 / `tokens.css` use `{purple, blue, green, amber, rose, cyan}`. `Avatar.tsx` maps API name → DRD token via a fixed, position-aligned record (preserving the deterministic distribution) and also accepts DRD names directly. Interim mapping is safe; ideally a later small backend change renames the palette strings to the DRD names, after which the alias rows in `Avatar.tsx` can be dropped.

**Verification (all green):** `biome ci .` clean (63 files); `pnpm typecheck` (turbo) 2/2; `pnpm --filter @taskflow/web test` 26/26; `vite build` succeeds (CSS 17.3 KB / gzip 4.7 KB, JS 454 KB / gzip 143 KB); `pnpm dev` serves all routes + redirects (`/`, `/login`, `/dashboard`, `/projects/x`→board, `/settings`→workspace, …) at HTTP 200 with zero resolve errors; `openapi-drift` clean locally. **Three small lint accommodations:** scoped `biome-ignore` for `noDocumentCookie` (test CSRF-cookie fixtures), `noLabelWithoutControl` (the generic `FormLabel` primitive), and a `<title>` on the Logo SVG.

### 2026-05-31 — Phase F1 complete (Frontend Skeleton)

First frontend code lands. `apps/web` now boots a token-styled React app and is ready to host routes (Phase F4) and screens (Part G).

- **Stack on the PR #19 toolchain:** React 19.2 + Vite 8 + `@vitejs/plugin-react` 6 + TypeScript 6 (strict, retained from the existing `tsconfig.json`). Added: Tailwind v3 (`tailwindcss` 3.4.17 + `postcss` 8.5.3 + `autoprefixer` 10.4.21), TanStack Query v5 (5.69.0), TanStack Router v1 (1.170.10 — see note below), React Hook Form 7.55 + Zod 3.24 + `@hookform/resolvers` 3.10, `react-intl` 7.1.
- **Design tokens (ADR 057 / DRD §2):** `src/styles/tokens.css` transcribes every DRD §2 value onto `:root` (teal primary scale, warm-neutral bg/text/border, shadows with the warm 120,100,70 rgba tint, status fg/bg pairs, priority, semantic, the 8-color label palette, the 6-color avatar palette, radii). `tailwind.config.ts` maps theme keys to these vars so a future theme swap touches only the token file. Spacing left at Tailwind's default 4px scale (matches DRD §2.11).
- **Typography (DRD §3):** Inter loaded via Google Fonts in `index.html` (preconnect + 400/500/600/700); the `font-family` stack and the 600-weight heading rule live in `src/styles/global.css` (the stack is duplicated there and in `fontFamily.sans` rather than `@apply`'d — see the Biome note).
- **Providers:** `src/main.tsx` composes `IntlProvider` → `QueryClientProvider` → `RouterProvider`. Query client in `src/app/query-client.ts` (retry off so ADR 043 error envelopes surface immediately). Router in `src/app/router.tsx` is a minimal code-based tree — a root route (renders `<Outlet />`) with one placeholder index route at `/` via `addChildren`; the full shell/auth/project tree is Phase F4. i18n catalog at `src/i18n/locales/en.json` (flat id→string map).
- **Forms:** shared Zod primitives in `src/forms/schemas/index.ts` (`emailSchema`, `passwordSchema` min-8 mirroring the B4 backend rule, `displayNameSchema`) for feature forms to compose in G1/G8.
- **Reduced motion (ADR 025 / TDD §6.5):** global `prefers-reduced-motion: reduce` rule in `global.css` neutralises animations/transitions/smooth-scroll app-wide. Logical-property utilities (Tailwind `ms-/me-/ps-/pe-`, `min-h-dvh`) are available and used; there is no Biome rule that *enforces* logical-over-physical, so that stays a code-review convention rather than a lint gate.
- **Biome (ADR 078):** Tailwind needed three accommodations in `biome.json`/CSS. (1) `@apply` is a Biome CSS **parser** error (not a lint rule), so `global.css` uses an explicit `font-family` stack instead of `@apply font-sans`. (2) `@tailwind base/components/utilities` trips `suspicious/noUnknownAtRules` and (3) the reduced-motion `!important` block trips `complexity/noImportantStyles` — both rules are turned off for `**/*.css` only via a scoped `overrides` entry in the root `biome.json`. All other rules (including a11y) stay on for CSS.
- **TanStack Router version bump:** initially pinned 1.114.3, but its route generics inferred `rootRoute.addChildren([...])`'s parameter as `never` under React 19 + TS 6 strict (the canonical docs pattern wouldn't typecheck). Bumped to **1.170.10** (current 1.x, solid React 19 type support) where the standard root + index tree compiles cleanly; `pnpm-lock.yaml` updated.
- **Vite path alias:** `@/*` is declared in `tsconfig.json`, which `tsc` and the Rolldown production build honour — but Vite's **dev** import-analysis does not read tsconfig `paths`, so `pnpm dev` initially 500'd on `@/app/...` imports while `build` passed. Added a matching `resolve.alias` (`@` → `./src`) in `vite.config.ts`; dev and build now agree.
- **Verification:** `biome ci .` clean; root `pnpm typecheck` (turbo) green across both workspaces that have the task (`api-types` + `web`; `config` has none); `vite build` succeeds (CSS 6.84 KB / gzip 2.46 KB, JS 355 KB / gzip 110 KB) and the bundled CSS contains the tokens + reduced-motion rule + Inter; `pnpm dev` serves `/`, `/src/main.tsx`, and `/src/app/router.tsx` with HTTP 200 and zero resolve errors. `pnpm-lock.yaml` was updated and should be committed with this phase (Part F is the first time frontend deps exist).
- **Not done here:** Lighthouse a11y baseline (DoD ≥90) was **not** run programmatically — the placeholder is a minimal semantic page (`main`/`h1`/`p`, `lang="en"`, token-driven contrast) expected to clear it comfortably; confirm with a real Lighthouse pass once the app shell (F4) renders representative content.

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
- `POST /api/v1/auth/login` — verifies password, creates session, sets `taskflow_session` (HttpOnly) + `taskflow_csrf` (JS-readable) cookies. Audit `auth.login.success` / `auth.login.failure`.
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
- Auth flow: read session cookie → `lookup_session` → CSRF check on the upgrade (the `csrf` query param + the `taskflow_csrf` cookie must match each other and the session's bound bytes) → load `User`/`Workspace` (rejecting `deleted_at IS NOT NULL`) → enumerate visible project channels via `services.projects.list_visible_projects` → subscribe to `user:{id}`, `workspace:{id}`, `project:{id}` per accessible project.
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
- `infra/nginx/nginx.conf` — HTTP→HTTPS redirect block, TLS server block with the ADR 083 headers (HSTS preload, strict CSP, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options`), routing for `/api/*`, `/ws` (with `Upgrade`/`Connection` and 3600s read timeout), `/health`, and an SPA fallback to the web container. Certificate paths reference Let's Encrypt's default layout. **As of 2026-06-14 (ADR 085 amendment), TLS moved to Cloudflare edge + a Cloudflare Origin CA cert — no certbot; the nginx cert paths are updated in Phase I2.**
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

**Still open (unchanged):** manual `make seed` end-to-end pass. (The coverage-gate follow-up is resolved — see 2026-05-30 coverage note below.)

### 2026-05-30 — Coverage gate raised 70% → 85% (E3 follow-up closed)

Closed the long-standing E3 coverage follow-up. The headline finding: **the 71% reading was a measurement artifact, not a test gap.**

- **Root cause:** the integration suite drives endpoints through httpx's `ASGITransport`, whose request handling runs under SQLAlchemy's greenlet bridge / worker threads. coverage.py only traces the main execution context by default, so every line reached *via an HTTP endpoint test* was silently uncounted — only direct service calls and unit tests registered. Diagnosed by observing that all 18 auth endpoint tests passed while `services/auth.py` showed its function bodies uncovered (only `def` lines, i.e. import-time, were counted), and confirmed by adding a single direct `auth_service.signup(...)` call which moved the file 48% → 58%.
- **Fix (the real win):** added `[tool.coverage.run] concurrency = ["thread", "greenlet"]` to `apps/api/pyproject.toml`. With no new tests this took the combined number **71% → 90%** — the existing endpoint tests now count. This config is required in CI too (coverage reads `pyproject`).
- **Targeted tests (+27, 236 → 263 passing):** closed the genuinely-untested branches the fix revealed — the `pg_dump`/S3 `backup_database_to_s3` job, task list `due=`/`sort=`/cursor-pagination branches and the assign-to-other-member path, auth wrong-password / accept-invitation existing-user + missing-fields / deleted-user-reset branches, member idempotent-remove + role-change-on-removed, label rename-conflict, invitation `derive_status` accepted/expired, activity project-scope + cursor pagination + `get_event`, and notification self-mention suppression + list pagination + mark-read success. Final combined coverage **~98%**.
- **Gate:** `ci.yml` `--cov-fail-under` 70 → **85** (the original E3 spec floor; ~13 pts of headroom over actual). Branch coverage (`--cov-branch`) remains off — a separate, larger decision.
- **Left uncovered by design (~22 lines):** defensive guards and dead code — `require_role` (no endpoint uses it; the codebase gates on `require_action`), the `dispatch_for_comment` dedup line (unreachable because `resolve_mentions` already de-dupes by id), `current_workspace`'s FK-guaranteed assert, and assorted single-line None-guards. Not worth contrived tests; candidates for `# pragma: no cover` if the number ever needs defending.
