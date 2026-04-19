# TaskFlow — Technical Design Document

**Version:** 1.0
**Date:** 2026-04-19
**Status:** Draft

---

## 1. Introduction

### 1.1 Purpose

This document defines the technical design of TaskFlow — the architecture, technology stack, infrastructure, and implementation patterns that realize the Business, Product, and Design requirements as working software. It translates the 87 Architectural Decision Records (ADRs) in `decisions/` into a coherent narrative that engineers can build from.

### 1.2 Scope

This TDD covers:
- The runtime architecture and AWS topology
- The repository layout and the two deployable applications (`apps/web`, `apps/api`)
- The data model, API shape, and real-time architecture
- Auth, security, observability, and deployment mechanics
- Local development and testing approach

It does **not** duplicate the PRD's feature behavior or the DRD's visual specification — it describes *how* those are built.

### 1.3 Reference Documents

| Document | Location |
|----------|----------|
| Business Requirements Document | [docs/business/business-requirements-document.md](../business/business-requirements-document.md) |
| Product Requirements Document | [docs/product/product-requirements-document.md](../product/product-requirements-document.md) |
| Design Requirements Document | [docs/design/design-requirements-document.md](../design/design-requirements-document.md) |
| Architectural Decision Records | [docs/technical/decisions/INDEX.md](decisions/INDEX.md) |

ADRs are cited inline as `(ADR NNN)` throughout this document.

---

## 2. Architecture Overview

### 2.1 One-paragraph description

TaskFlow is a single-tenant cloud-hosted SaaS (ADR 002, 003) delivered as a web-only application (ADR 001). It runs as a set of Docker containers on one AWS EC2 `t4g.small` instance in `us-east-1` (ADR 036, 037), with PostgreSQL co-located on the same host (ADR 033). The frontend is a React SPA built by Vite (ADR 029, 030, 031) that talks to a FastAPI backend (ADR 032) over a versioned REST API (ADR 040, 041) and a WebSocket channel for real-time updates (ADR 044). Postgres `LISTEN/NOTIFY` fans out real-time events across WebSocket handlers (ADR 045). All AWS resources are defined in CloudFormation (ADR 087); GitHub Actions builds, tests, and deploys (ADR 071).

### 2.2 Key design principles

1. **Do the simpler thing.** This is a demonstration project with a single contributor. Every service, subscription, or dependency must justify its complexity against the alternative of not having it.
2. **Consolidate services.** One EC2 host runs the web, API, and database. No Redis, no RDS, no ALB, no ECS control plane. This trades scalability headroom for operational simplicity.
3. **No third-party observability.** CloudWatch is the single observability plane (ADR 075–077). Avoids another vendor and another set of secrets.
4. **AWS-native where possible.** SES for email (ADR 067), Parameter Store for secrets (ADR 073), CloudFormation for IaC (ADR 087). Reduces cross-account and cross-vendor surface.
5. **Future-ready but not future-built.** The code is written so that additional locales (ADR 018), a public API (ADR 013), a horizontally scaled deploy (ADR 045), and custom workflows (BRD §9) can be added without rearchitecture — but none of that work is done now.
6. **Typed everywhere.** Strict TypeScript on the frontend (ADR 027), Pydantic v2 on the backend (ADR 042), types generated from the OpenAPI schema flow into the client (ADR 042). The type system is a primary bug-detection tool.
7. **Tests hit real systems.** Integration tests run against a real Postgres (ADR 079); E2E tests run against a full `docker compose up` stack (ADR 080). Mocks are confined to the unit-test layer.

### 2.3 System context diagram

```
┌──────────────┐       ┌───────────────────────────────────────────────┐
│              │       │                    Internet                   │
│    User      │◄─────►│                                               │
│  (browser)   │       │                                               │
└──────────────┘       └───────┬───────────────────────────────────────┘
                               │ HTTPS / WSS
                               ▼
                       ┌─────────────────┐
                       │   Route 53      │─────► taskflow.{domain}
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Elastic IP    │
                       └────────┬────────┘
                                │
              ┌─────────────────▼─────────────────┐
              │    EC2 t4g.small (us-east-1)      │
              │    Docker Compose                 │
              │                                   │
              │  ┌──────────────────────────────┐ │
              │  │ nginx  (:443, :80→:443)      │ │
              │  │  • TLS (Let's Encrypt)       │ │
              │  │  • Static /  → web container │ │
              │  │  • /api     → api container  │ │
              │  │  • /ws      → api container  │ │
              │  │  • Security headers          │ │
              │  └─────┬────────────────┬───────┘ │
              │        │                │         │
              │  ┌─────▼──────┐  ┌──────▼──────┐  │
              │  │    web     │  │     api     │  │
              │  │ nginx:80   │  │  FastAPI +  │  │
              │  │ SPA assets │  │  Uvicorn    │  │
              │  │            │  │  :8000      │  │
              │  └────────────┘  └──────┬──────┘  │
              │                         │         │
              │                   ┌─────▼──────┐  │
              │                   │ PostgreSQL │  │
              │                   │     16     │  │
              │                   └────────────┘  │
              └────────────┬─────────┬────────────┘
                           │         │
          ┌────────────────┘         └─────────────────┐
          │                                            │
          ▼                                            ▼
 ┌─────────────────┐                          ┌─────────────────┐
 │ SSM Parameter   │                          │ S3 (backups)    │
 │ Store (Secure)  │                          │ lifecycle=30d   │
 └─────────────────┘                          └─────────────────┘
 ┌─────────────────┐                          ┌─────────────────┐
 │ CloudWatch      │                          │ SES             │
 │ Logs / Alarms   │                          │ Transactional   │
 │ SNS → email     │                          │ Email           │
 └─────────────────┘                          └─────────────────┘
 ┌─────────────────┐                          ┌─────────────────┐
 │ ECR             │                          │ GitHub Actions  │
 │ Container Reg.  │◄─────── pushes ──────────│ CI / CD         │
 └─────────────────┘                          └─────────────────┘
```

---

## 3. Technology Stack

### 3.1 Runtime stack

| Layer | Choice | ADR |
|-------|--------|-----|
| Frontend language | TypeScript 5.x (strict mode) | 027 |
| Frontend framework | React 18+ | 029 |
| Frontend rendering | SPA (client-side) | 030 |
| Build tooling | Vite 5+ | 031 |
| Server state | TanStack Query v5 | 053 |
| Client state | Zustand + React Context | 054 |
| Routing | TanStack Router v1 | 055 |
| Forms | React Hook Form + Zod | 056 |
| Styling | Tailwind CSS v3 over CSS custom properties | 057, 022 |
| Component primitives | Radix UI (shadcn/ui pattern) | 058 |
| Drag and drop | `@dnd-kit/core` | 059 |
| Markdown | `react-markdown` + `remark-gfm` + `rehype-sanitize` | 060 |
| Internationalization | `react-intl` (FormatJS / ICU) | 061 |
| Backend language | Python 3.12+ | 028 |
| Backend framework | FastAPI + Uvicorn (ASGI) | 032 |
| Validation | Pydantic v2 | 042 |
| ORM / Core | SQLAlchemy 2.0 async + asyncpg | 034 |
| Migrations | Alembic | 035 |
| Background jobs | FastAPI BackgroundTasks + APScheduler | 069 |
| Real-time fan-out | `broadcaster` (Postgres backend) | 045 |
| Password hashing | `argon2-cffi` | 048 |
| Rate limiting | `slowapi` | 052 |
| Database | PostgreSQL 16 | 033 |
| Reverse proxy | nginx | 036, 083 |
| TLS | Let's Encrypt via certbot | 085 |

### 3.2 Platform and tooling

| Concern | Choice | ADR |
|---------|--------|-----|
| Cloud provider | AWS (us-east-1) | 036, 037 |
| Compute | EC2 `t4g.small` (ARM64, 2 vCPU, 2 GB) | 036 |
| Infrastructure as Code | CloudFormation | 087 |
| CI/CD | GitHub Actions | 071 |
| CI secrets | GitHub Secrets + OIDC federation | 073 |
| Runtime secrets | AWS SSM Parameter Store (SecureString) | 073 |
| Container registry | Amazon ECR | 038 |
| Email delivery | Amazon SES | 067 |
| DNS | Route 53 | 036 |
| Backups | `pg_dump` → S3 with 30-day lifecycle | 074 |
| Logging / metrics | CloudWatch Logs + Agent | 075 |
| Error tracking | CloudWatch Logs metric filters | 076 |
| Uptime | CloudWatch alarms → SNS email | 077 |
| Linting / formatting | Biome (TS), Ruff (Python) | 078 |
| Unit / integration tests | Vitest, pytest + pytest-asyncio | 079 |
| E2E | Playwright | 080 |
| Accessibility | `@axe-core/playwright`, `vitest-axe` | 081 |
| Dependency scanning | GitHub Dependabot + CodeQL | 086 |

---

## 4. Repository Structure

The codebase is a pnpm workspaces monorepo with Turborepo build orchestration (ADR 026). One repository holds frontend, backend, shared packages, and infrastructure.

```
taskflow/
├── apps/
│   ├── web/                          # React SPA
│   │   ├── src/
│   │   │   ├── app/                  # TanStack Router route tree
│   │   │   ├── components/
│   │   │   │   ├── ui/               # shadcn-style Radix wrappers
│   │   │   │   ├── board/
│   │   │   │   ├── task/
│   │   │   │   ├── project/
│   │   │   │   └── ...
│   │   │   ├── features/             # Feature-scoped logic
│   │   │   │   ├── auth/
│   │   │   │   ├── notifications/
│   │   │   │   ├── realtime/
│   │   │   │   └── ...
│   │   │   ├── api/                  # Generated client + hooks
│   │   │   ├── forms/
│   │   │   │   └── schemas/          # Zod schemas
│   │   │   ├── styles/
│   │   │   │   └── tokens.css        # DRD design tokens
│   │   │   ├── locales/              # react-intl messages
│   │   │   ├── lib/
│   │   │   └── main.tsx
│   │   ├── Dockerfile                # multi-stage, arm64
│   │   ├── index.html
│   │   ├── tailwind.config.ts
│   │   ├── vite.config.ts
│   │   └── package.json
│   │
│   └── api/                          # FastAPI backend
│       ├── taskflow/
│       │   ├── main.py               # FastAPI app entry point
│       │   ├── settings.py           # Pydantic Settings from env / SSM
│       │   ├── db/
│       │   │   ├── session.py
│       │   │   ├── models/           # SQLAlchemy ORM models
│       │   │   └── migrations/       # Alembic versions
│       │   ├── api/
│       │   │   └── v1/
│       │   │       ├── auth.py
│       │   │       ├── workspaces.py
│       │   │       ├── projects.py
│       │   │       ├── tasks.py
│       │   │       ├── comments.py
│       │   │       ├── labels.py
│       │   │       ├── notifications.py
│       │   │       ├── search.py
│       │   │       ├── activity.py
│       │   │       └── ws.py         # WebSocket endpoint
│       │   ├── schemas/              # Pydantic DTOs
│       │   ├── services/             # Business logic
│       │   ├── auth/                 # Session, CSRF, password, permissions
│       │   ├── realtime/             # broadcaster + channel helpers
│       │   ├── scripts/
│       │   │   └── seed.py
│       │   └── tasks/                # APScheduler jobs
│       ├── tests/
│       │   ├── unit/
│       │   └── integration/
│       ├── Dockerfile                # arm64, python:3.12-slim
│       ├── alembic.ini
│       ├── pyproject.toml
│       └── ruff.toml
│
├── packages/                         # Shared across apps
│   ├── api-types/                    # Generated from OpenAPI
│   └── config/                       # Shared tsconfig, eslint-like configs
│
├── infra/
│   ├── cloudformation/
│   │   ├── network.yml
│   │   ├── compute.yml
│   │   ├── storage.yml
│   │   ├── container-registry.yml
│   │   ├── parameters.yml
│   │   ├── monitoring.yml
│   │   ├── dns.yml
│   │   ├── email.yml
│   │   └── iam.yml
│   ├── nginx/
│   │   └── nginx.conf
│   └── ec2/
│       └── user-data.sh              # Instance bootstrap
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── docker-compose.yml                # local dev
├── docker-compose.prod.yml           # production
├── docker-compose.test.yml           # integration/E2E fixtures
├── Makefile                          # dev, test, migrate, seed, deploy shortcuts
├── turbo.json
├── pnpm-workspace.yaml
├── biome.json
└── package.json
```

### 4.1 Shared code

Despite the cross-language split (ADR 027, 028), some artifacts are shared:

- **`packages/api-types`** — TypeScript types generated from the FastAPI OpenAPI schema via `openapi-typescript`. Regenerated in CI and committed; drift between this file and the backend becomes a PR diff.
- **Validation** — Pydantic on the server, Zod on the client. These are authored in parallel and kept in sync by code review and integration tests (ADR 042, 056).

---

## 5. Infrastructure & Deployment Topology

### 5.1 AWS resources

All resources are provisioned via CloudFormation (ADR 087) organized into small, composable stacks:

| Stack | Purpose | Key resources |
|-------|---------|---------------|
| `network` | VPC and networking | VPC, public subnet, internet gateway, route table, security group (allow 22/SSM + 80/443 from internet; all outbound) |
| `compute` | The host | `t4g.small` EC2, Elastic IP, IAM instance profile, user-data installing Docker + CloudWatch Agent |
| `container-registry` | Image hosting | ECR repositories `taskflow/api`, `taskflow/web` with lifecycle policy (keep last 10 tagged, expire untagged after 7 days) |
| `storage` | Persistence beyond the disk | S3 bucket for Postgres backups (SSE-S3, 30-day lifecycle), S3 bucket for source maps |
| `parameters` | Config | SSM Parameter Store SecureString parameters under `/taskflow/prod/*` (values set out-of-band via CLI; stack manages names and KMS policy) |
| `email` | Transactional email | SES verified domain identity, DKIM records |
| `monitoring` | Observability | CloudWatch log groups, metric filters, alarms, SNS topic `taskflow-alerts` |
| `dns` | DNS | Route 53 hosted zone, A record → Elastic IP, MX/TXT for SES, ACM cert (unused by this topology but provisioned for future HTTPS-via-ALB migration) |
| `iam` | Deploy identity | OIDC provider for GitHub Actions; `taskflow-deploy-role` with narrow permissions (ECR push, CloudFormation deploy, SSM Run Command) |

### 5.2 Single-host topology

The EC2 instance runs three containers via `docker-compose.prod.yml`:

- **`nginx`** — public entry on `:80` and `:443`. Terminates TLS with a Let's Encrypt certificate (ADR 085). Routes:
  - `/api/*` → `api:8000`
  - `/ws` → `api:8000` (WebSocket upgrade)
  - everything else → `web:80` (static assets)
  - Applies security headers (ADR 083) on every response.
- **`api`** — FastAPI + Uvicorn on `:8000`. Reads runtime config from environment variables populated at boot from Parameter Store.
- **`web`** — a tiny nginx serving the Vite-built static assets.
- **`db`** — PostgreSQL 16 with a named Docker volume mapped to `/var/lib/postgresql/data` on the host.

### 5.3 Capacity planning

A `t4g.small` has 2 GB RAM. Rough allocation at idle:

| Component | Expected resident memory |
|-----------|--------------------------|
| PostgreSQL 16 (`shared_buffers=256MB`) | ~350 MB |
| FastAPI + Uvicorn (2 workers) | ~350 MB |
| nginx × 2 (public + web) | ~30 MB |
| Host OS / Docker daemon | ~500 MB |
| Headroom | ~750 MB |

Scaling plan if capacity becomes tight:

1. **First move:** extract Postgres to RDS `db.t4g.micro` or `db.t4g.small`. Frees ~500 MB on the app host.
2. **Second:** move to `t4g.medium` (4 GB) or `t4g.large` (8 GB). Vertical-only until horizontal becomes necessary.
3. **Third (horizontal):** switch the real-time backend (ADR 045) from in-process to multi-node by pointing `broadcaster` at Redis (via ElastiCache) or by relying on Postgres `LISTEN/NOTIFY` across multiple FastAPI processes (already supported). Rate-limiting (`slowapi`) moves to a shared backend.

None of these are in scope for the demonstration launch.

### 5.4 TLS and domain

Let's Encrypt certificates are provisioned and renewed by a `certbot` container that shares the nginx conf and cert directories (ADR 085). Renewal runs daily; nginx reload is triggered on new certs.

DNS is Route 53 in the same AWS account. An `A` record points `taskflow.{domain}` at the Elastic IP.

---

## 6. Frontend Architecture

### 6.1 Application shell

The app is a single-page application (ADR 030). `index.html` contains only the app root div; React hydrates at startup. The shell, defined in `apps/web/src/app/_shell.tsx`, implements the three-zone layout from DRD §6.1:

- **Global header** (52 px) — breadcrumbs, search, notification bell, user menu.
- **Sidebar** (240 px desktop; icon-only at tablet; slide-out on mobile).
- **Content area** — the outlet for the active route.

The shell is rendered for every authenticated route; login, signup, and invitation-accept pages are outside the shell.

### 6.2 Routing (ADR 055)

TanStack Router owns the URL. Route definitions mirror the page inventory in DRD §19:

```
/login
/signup
/accept-invite
/                               → redirects to /dashboard if authed
/dashboard
/projects/:projectId            → board view (default)
/projects/:projectId/list       → list view
/projects/:projectId/tasks/:taskId   → board/list with task panel open
/notifications
/settings
    /workspace
    /members
    /labels
    /profile
```

Search parameters are typed. Filter state (`status`, `assignee`, `priority`, `label`, `due`) is owned by the URL and shared between board and list (PRD §12.2). The task detail panel is a nested route — the panel overlay mounts when `/tasks/:taskId` is matched; closing the panel navigates back to the parent route.

### 6.3 Data flow and state

| State kind | Owner | ADR |
|-----------|-------|-----|
| Server state (queries / mutations) | TanStack Query | 053 |
| URL state (filters, panel, view) | TanStack Router | 055 |
| Global UI (toasts, command menu) | Zustand | 054 |
| Auth identity (current user, role) | React Context (populated by a bootstrap query) | 054 |
| Form state (in-progress edits) | React Hook Form (local to form) | 056 |

The real-time bridge subscribes the client to the `/ws` channel on login and translates inbound events into TanStack Query cache updates:

```
WebSocket event → realtime dispatcher:
  • { type: 'task.updated', task }   → queryClient.setQueryData(['task', task.id], task)
                                       + invalidate board queries for the task's project
  • { type: 'task.created', task }   → invalidate ['project', pid, 'tasks']
  • { type: 'comment.created', c }   → invalidate ['task', c.task_id, 'comments']
  • { type: 'notification', n }      → prepend to ['notifications'] + increment badge
  • { type: 'activity', a }          → prepend to ['activity', scope]
```

Optimistic drag-and-drop (ADR 046) uses TanStack Query's `onMutate`/`onError`/`onSettled` — the card visually moves before the server confirms; on error the card snaps back and a toast explains.

### 6.4 Component architecture

Three tiers:

- **UI primitives** (`src/components/ui/`) — Radix-backed, Tailwind-styled, shadcn-style. Examples: `Button`, `Dialog`, `DropdownMenu`, `Select`, `Toast`, `Tabs`, `Checkbox`.
- **Domain components** (`src/components/{board,task,project,...}/`) — features assembled from primitives. Examples: `BoardColumn`, `TaskCard`, `TaskDetailPanel`, `CommentList`.
- **Route components** (`src/app/...`) — thin composition of domain components; owns queries and URL state.

### 6.5 Styling pipeline (ADR 057)

- `src/styles/tokens.css` declares every design token from DRD §2 as a CSS custom property on `:root`.
- `tailwind.config.ts` maps Tailwind's theme keys to those variables:
  ```ts
  theme: {
    colors: { primary: 'var(--primary)', bg: 'var(--bg-app)', ... },
    spacing: { 1: '4px', 2: '8px', ... },
    boxShadow: { card: 'var(--shadow-card)', ... },
  }
  ```
- Logical properties (ADR 019) use Tailwind's `ms-*`, `me-*`, `ps-*`, `pe-*`, `start-*`, `end-*`.
- A single global rule handles reduced motion:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      transition-duration: 0ms !important;
      animation-duration: 0ms !important;
    }
  }
  ```

### 6.6 Markdown rendering (ADR 060)

`<Markdown>` is a wrapper around `react-markdown` with a fixed rehype/remark pipeline:

```
remark-parse → remark-gfm → remark-mentions (custom)
→ remark-rehype → rehype-sanitize (strict allowlist) → rehype-react
```

- Links open in new tabs with `rel="noopener noreferrer nofollow"`.
- Inline HTML and raw HTML blocks are stripped.
- `@mentions` are detected pre-render against the workspace member list; unknown handles remain plain text.

### 6.7 Internationalization (ADR 061)

`react-intl` provides `<IntlProvider>` at the app root. Messages authored as ICU MessageFormat in `src/locales/en.json`. Dates, times, numbers, and relative times use native `Intl.*` APIs via small formatter helpers. English is the only bundled locale at launch; additional locales will be lazy-loaded.

### 6.8 Build pipeline (ADR 031)

Vite produces hashed static assets. The Docker image for `web` uses a multi-stage build:

```dockerfile
FROM node:20-alpine AS build
WORKDIR /build
COPY . .
RUN pnpm install --frozen-lockfile && pnpm --filter web build

FROM nginx:1.27-alpine
COPY --from=build /build/apps/web/dist /usr/share/nginx/html
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
```

All images are built `linux/arm64` to match the `t4g.small` host (ADR 038).

---

## 7. Backend Architecture

### 7.1 FastAPI application structure

`apps/api/taskflow/main.py` is the FastAPI entry point. At startup it:

1. Loads settings via `pydantic-settings` (env vars populated from Parameter Store by the entrypoint).
2. Creates the SQLAlchemy async engine.
3. Runs Alembic migrations to the latest head (fails fast on migration errors).
4. Starts APScheduler for periodic jobs (ADR 069).
5. Connects the `broadcaster` instance to Postgres for real-time fan-out.
6. Mounts routers under `/api/v1` and the WebSocket endpoint at `/ws`.

### 7.2 Layered architecture

```
api/v1/   routes   ── FastAPI routers, dependency injection, request/response Pydantic DTOs
             │
             ▼
services/          ── Business logic. Workspace-scoped operations.
             │        Transactions, permission checks, audit log writes,
             │        notification fan-out, activity event writes.
             ▼
db/models/         ── SQLAlchemy ORM models.
db/session.py      ── Async session factory, dependency.
```

Routes are thin — they parse, dispatch to a service, and serialize. Services are the testable unit of business logic. ORM models never cross the API boundary — DTOs are distinct (ADR 034).

### 7.3 Dependency injection

FastAPI's `Depends` threads request-scoped dependencies through handlers:

- `get_db()` — an async session bound to a single request transaction.
- `current_session()` — reads the session cookie, looks up the active session row, returns it (or 401).
- `current_user()` — depends on `current_session`, returns the `User` model.
- `current_workspace()` — returns the user's workspace (TaskFlow is one-workspace-per-user; ADR PRD §4.1).
- `require_role(*roles)` — returns a dependency factory that enforces a role floor.
- `require_project_access(project_id_param)` — enforces project-level access (ADR PRD §5.2).
- `verify_csrf()` — for state-changing requests (ADR 051).

Handlers compose these to make permission enforcement declarative:

```python
@router.post("/projects/{project_id}/tasks", response_model=TaskRead)
async def create_task(
    project_id: UUID,
    body: TaskCreate,
    user: User = Depends(current_user),
    _: None = Depends(require_role("owner", "admin", "member")),
    __: None = Depends(require_project_access("project_id")),
    ___: None = Depends(verify_csrf),
    db: AsyncSession = Depends(get_db),
) -> TaskRead:
    return await task_service.create(db, user, project_id, body)
```

### 7.4 Background jobs (ADR 069)

Two mechanisms, no separate worker process:

- **`BackgroundTasks`** for fire-and-forget in-request work — primarily sending email after a commit. Example: invitation creation commits, the response returns, SES is called from a background task so the user doesn't wait on network to SES.
- **APScheduler** `AsyncIOScheduler` inside the FastAPI process for periodic jobs:

| Job | Cadence |
|-----|---------|
| Expire invitations older than 7 days | every 15 minutes |
| Delete expired sessions | daily at 04:00 UTC |
| Delete expired password-reset tokens | daily at 04:00 UTC |
| `pg_dump` to S3 | daily at 03:00 UTC |

---

## 8. Data Model

### 8.1 Entity overview

```
workspaces ─┬─── users ────── sessions
            │       │
            │       ├──────── invitations
            │       │
            │       └──────── password_reset_tokens
            │
            ├─── projects ──┬─── project_memberships
            │               │
            │               └─── tasks ──┬── comments
            │                            │
            │                            └── task_labels ─── labels
            │
            ├─── activity_events
            ├─── notifications
            └─── audit_log
```

### 8.2 Core tables

Identifiers are UUIDv7 (time-ordered, index-friendly). Every row has `created_at timestamptz` default `now()`; most mutable rows also have `updated_at`.

#### `workspaces`

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `name` | `text` | Editable by Owner/Admin |
| `created_by` | `uuid` FK → users | |
| `created_at` | `timestamptz` | |

#### `users`

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `workspace_id` | `uuid` FK | one workspace per user |
| `email` | `citext` | unique within workspace when `deleted_at` is null |
| `name` | `text` | |
| `role` | `text` | `owner`, `admin`, `member`, `viewer` |
| `password_hash` | `text` | Argon2id (ADR 048), nullable after deletion |
| `deleted_at` | `timestamptz`, nullable | in-place anonymization flag (ADR 065) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

Partial unique index: `(workspace_id, lower(email)) WHERE deleted_at IS NULL`.

#### `sessions` (ADR 047)

| Column | Type | Notes |
|--------|------|-------|
| `id` | `bytea` PK | SHA-256 of the session token |
| `user_id` | `uuid` FK | |
| `csrf_token` | `bytea` | 32 random bytes (ADR 051) |
| `expires_at` | `timestamptz` | absolute lifetime 30d |
| `last_seen_at` | `timestamptz` | idle timeout 7d |
| `ip` | `inet` | |
| `user_agent` | `text` | |
| `created_at` | `timestamptz` | |

Indexes: `(user_id)`, `(expires_at)` for cleanup.

#### `invitations`

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `workspace_id` | `uuid` FK | |
| `email` | `citext` | |
| `role` | `text` | assigned role |
| `token_hash` | `bytea` | SHA-256 of the invitation token |
| `invited_by` | `uuid` FK → users | |
| `expires_at` | `timestamptz` | 7 days (PRD §3.3) |
| `accepted_at` | `timestamptz`, nullable | |
| `created_at` | `timestamptz` | |

#### `password_reset_tokens`

| Column | Type |
|--------|------|
| `token_hash` PK | `bytea` |
| `user_id` FK | `uuid` |
| `expires_at` | `timestamptz` (1h) |
| `used_at` | `timestamptz`, nullable |
| `created_at` | `timestamptz` |

#### `projects`

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `workspace_id` | `uuid` FK | |
| `name` | `text` | |
| `description` | `text` | |
| `color` | `text` | from the project-color palette (sidebar dot) |
| `created_by` | `uuid` FK → users | |
| `created_at`, `updated_at` | `timestamptz` | |

#### `project_memberships`

Resolves project-level access (PRD §5.2).

| Column | Type |
|--------|------|
| `project_id` FK | `uuid` |
| `user_id` FK | `uuid` |
| `added_at` | `timestamptz` |

Primary key `(project_id, user_id)`.

#### `tasks`

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `project_id` | `uuid` FK | |
| `workspace_id` | `uuid` FK | denormalized for fast workspace-scoped queries |
| `title` | `text` | |
| `description` | `text` | Markdown (ADR 014) |
| `status` | `text` | enum: `backlog`, `todo`, `in_progress`, `in_review`, `done`, `cancelled` |
| `priority` | `text` | `none`, `low`, `medium`, `high`, `urgent` |
| `assignee_id` | `uuid` FK → users, nullable | |
| `due_date` | `date`, nullable | end-of-day in user TZ (PRD §6.4) |
| `created_by` | `uuid` FK → users | |
| `created_at`, `updated_at` | `timestamptz` | |
| `search_vector` | `tsvector` (generated) | FTS (ADR 062) |

Indexes: `(project_id, status, created_at DESC)`, `(assignee_id, due_date)`, GIN on `search_vector`.

#### `labels`

| Column | Type |
|--------|------|
| `id` PK | `uuid` |
| `workspace_id` FK | `uuid` |
| `name` | `text` |
| `color` | `text` (from fixed palette) |
| `created_at` | `timestamptz` |

#### `task_labels`

Join table; PK `(task_id, label_id)`.

#### `comments`

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `task_id` | `uuid` FK | |
| `author_id` | `uuid` FK → users | |
| `body` | `text` | Markdown |
| `created_at`, `updated_at` | `timestamptz` | |

#### `activity_events` (ADR 063)

Append-only.

| Column | Type |
|--------|------|
| `id` PK | `uuid` |
| `workspace_id` FK | `uuid` |
| `project_id` FK | `uuid`, nullable |
| `actor_id` FK | `uuid` |
| `event_type` | `text` — `task.created`, `task.status_changed`, `task.assigned`, `task.unassigned`, `comment.created` |
| `subject_type` | `text` |
| `subject_id` | `uuid` |
| `metadata` | `jsonb` |
| `created_at` | `timestamptz` |

Indexes: `(workspace_id, created_at DESC)`, `(project_id, created_at DESC)`, `(actor_id, created_at DESC)`.

#### `notifications` (ADR 064)

| Column | Type |
|--------|------|
| `id` PK | `uuid` |
| `recipient_id` FK | `uuid` |
| `actor_id` FK | `uuid` |
| `event_type` | `text` — `mention`, `task_assigned`, `task_status_changed`, `task_commented` |
| `task_id` FK | `uuid` |
| `project_id` FK | `uuid` |
| `metadata` | `jsonb` |
| `read_at` | `timestamptz`, nullable |
| `created_at` | `timestamptz` |

Indexes: `(recipient_id, created_at DESC)`; partial `(recipient_id) WHERE read_at IS NULL` for the unread-badge query.

#### `audit_log` (ADR 084)

Append-only; see ADR 084 for the enumerated event types and shape.

### 8.3 Workspace isolation

Every workspace-scoped table carries `workspace_id`. The service layer has a `require_workspace` helper that asserts the row's `workspace_id` matches the caller's. Any SELECT/UPDATE/DELETE at the service layer must filter by `workspace_id` — this is enforced by lint-like checks in code review and by integration tests that attempt cross-workspace access. This is the primary defense against the single-tenant logical-isolation risk (ADR 003).

### 8.4 Migrations (ADR 035)

Alembic versions live in `db/migrations/versions/`. Each migration is reviewed and hand-edited after autogeneration. Migrations run on container startup via an entrypoint script; the deploy workflow (§11) can run them as a separate step in advance to allow zero-downtime schema-safe migrations in the future.

---

## 9. API Design

### 9.1 Conventions (ADR 040, 041)

- All endpoints under `/api/v1/`.
- Resource-oriented URLs. Example: `GET /api/v1/projects/:id/tasks`, `POST /api/v1/tasks/:id/comments`.
- JSON request and response bodies; `Content-Type: application/json`.
- Methods: `GET` safe; `POST` create; `PATCH` partial update; `PUT` full replace; `DELETE` remove. Idempotency where HTTP semantics demand it.
- Pagination: cursor-based for list endpoints (`?cursor=...&limit=50`), never offset. Cursors opaque to clients.
- Authenticated via session cookie (ADR 047); state-changing requests also require the CSRF header (ADR 051).

### 9.2 Error contract (ADR 043)

All error responses follow:

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "No task with that id exists in this workspace.",
    "fields": { "title": ["REQUIRED"] }
  }
}
```

`code` is machine-readable and stable. The frontend maps codes to translated copy. Validation failures (422) populate `fields`.

Global exception handlers in `taskflow/errors.py` convert internal exceptions and Pydantic `ValidationError` into this envelope. Unhandled exceptions produce a 500 and are logged at ERROR level (ADR 076).

### 9.3 OpenAPI and type generation

FastAPI generates an OpenAPI 3.1 document from the Pydantic request/response models. This document is:

- Exposed at `/api/v1/openapi.json` (accessible only from localhost / authed admin; not publicly routed in prod).
- Consumed by `openapi-typescript` in the frontend build to produce `packages/api-types/schema.d.ts`.
- Reviewed in CI — a diff against the committed types is treated as a deliberate API change.

### 9.4 Endpoint inventory (summary)

Auth:
- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/logout`
- `POST /auth/password-reset/request`
- `POST /auth/password-reset/confirm`
- `GET /auth/me`

Workspace:
- `GET /workspaces/me`
- `PATCH /workspaces/me`
- `GET /workspaces/me/members`
- `PATCH /workspaces/me/members/:userId` — role change
- `DELETE /workspaces/me/members/:userId` — remove user
- `GET /workspaces/me/invitations`
- `POST /workspaces/me/invitations`
- `POST /workspaces/me/invitations/:id/resend`

Projects:
- `GET /projects`
- `POST /projects`
- `GET /projects/:id`
- `PATCH /projects/:id`
- `GET /projects/:id/access` / `POST` / `DELETE`

Tasks:
- `GET /projects/:id/tasks`
- `POST /projects/:id/tasks`
- `GET /tasks/:id`
- `PATCH /tasks/:id`
- `PATCH /tasks/:id/status`
- `POST /tasks/:id/comments`
- `GET /tasks/:id/comments`

Labels:
- `GET /labels`
- `POST /labels`
- `PATCH /labels/:id`
- `DELETE /labels/:id`

Feed and notifications:
- `GET /activity?project_id=...`
- `GET /notifications`
- `POST /notifications/mark-all-read`
- `POST /notifications/:id/read`

Search:
- `GET /search?q=...`

Dashboard:
- `GET /dashboard/my-tasks`
- `GET /dashboard/projects`

---

## 10. Real-Time Architecture

### 10.1 Connection lifecycle (ADR 044)

1. On login, the SPA calls `GET /auth/me` and receives the current user.
2. The SPA opens a WebSocket to `wss://{host}/ws`. The session cookie is sent automatically; a CSRF token is included as a query string per ADR 051.
3. The server's WebSocket handler authenticates via the session dependency (§7.3) and subscribes the connection to two channels:
   - `user:{user_id}` — notifications for this user.
   - `workspace:{workspace_id}` — workspace-wide activity.
   - For each project the user has access to, `project:{project_id}` — for board and task updates.
4. On any project-access change (e.g., an admin grants or revokes access), the server sends a control message; the client reconnects to refresh its subscriptions.

### 10.2 Publishing (ADR 045, 070)

Mutation flow:

1. Service layer opens a DB transaction.
2. Persists the mutation (e.g., task update).
3. Writes the corresponding `activity_events` row.
4. Writes any `notifications` rows (respecting the self-trigger rule per PRD §15.1).
5. `COMMIT`.
6. After commit, the service publishes messages via `broadcaster.publish(channel, envelope)`. `broadcaster` translates this into Postgres `NOTIFY`.
7. Any FastAPI process with WebSocket handlers subscribed to that channel receives the NOTIFY and pushes to connected clients.

Envelope:

```json
{
  "type": "task.updated",
  "workspace_id": "...",
  "project_id": "...",
  "payload": { ... task-shaped DTO ... },
  "emitted_at": "2026-04-19T18:22:00Z"
}
```

### 10.3 Consumption on the client

See §6.3. Each inbound event runs through a single dispatcher that either calls `queryClient.setQueryData` (precision update) or `queryClient.invalidateQueries` (refetch trigger). Toast notifications are surfaced only for a small whitelist (e.g., incoming `@mention` while the task is not visible).

### 10.4 Delivery semantics

- **At-most-once** for ephemeral messages. If a client is disconnected when a NOTIFY fires, the message is not replayed. The next query (e.g., opening the notifications page) reconciles state from the database.
- **Reconnect strategy**: exponential backoff up to 30 s, jittered. On reconnect, the client invalidates all queries to resync.

---

## 11. Authentication & Authorization

### 11.1 Sign-up and login

- Sign-up creates a new workspace and its Owner atomically in one transaction. Passwords are hashed with Argon2id (ADR 048) using parameters `time_cost=3, memory_cost=65536, parallelism=4`.
- Login verifies the password, creates a `sessions` row, and sets two cookies on the response:
  - `taskflow_session` — session id, `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`, 30-day expiry.
  - `csrf_token` — random token, `Secure`, `SameSite=Lax`, `Path=/`, readable by JS.
- Responses to successful auth mutations include the current user DTO to populate the client cache without a second round trip.

### 11.2 Session enforcement (ADR 047)

Every authenticated endpoint depends on `current_session`. Implementation:

1. Read `taskflow_session` cookie.
2. Hash it and look up the row.
3. Reject if missing, expired, or `user.deleted_at is not null`.
4. Update `last_seen_at`. Reject if idle for more than 7 days.
5. Return the session row.

### 11.3 CSRF protection (ADR 051)

For every `POST`, `PUT`, `PATCH`, `DELETE`:

1. Read the `csrf_token` cookie.
2. Read the `X-CSRF-Token` request header.
3. Compare byte-for-byte; reject 403 on mismatch.
4. Further verify the token matches the session row's bound CSRF value.

`GET`/`HEAD`/`OPTIONS` skip CSRF. WebSocket upgrades include the CSRF token in a query parameter and are validated once at connect.

### 11.4 Password reset (ADR 049)

Documented in ADR 049. Key properties: no account enumeration, 1-hour token lifetime, single-use, and session revocation on successful reset.

### 11.5 Authorization model (PRD §2.1)

Authorization is enforced in two layers:

**Workspace-level role.** Four roles: `owner`, `admin`, `member`, `viewer`. The `require_role` dependency asserts the caller's role is in the allowed set.

**Project-level access.** A `project_memberships` table resolves which users can see which projects. The `require_project_access` dependency checks that the caller has a row in that table (or is an `owner`/`admin`, who have implicit access to all projects).

Both checks must pass. Permission code lives in `auth/permissions.py` with unit tests for every combination of role × action × project-access.

### 11.6 Invitation acceptance (ADR 011, PRD §3.3)

1. Recipient clicks the email link with the raw token.
2. SPA POSTs `/auth/accept-invitation` with the token + optional new account fields.
3. Backend hashes, looks up, verifies not expired/consumed.
4. If the email matches an existing user row, add them to the workspace (no new user created).
5. If no existing user, create user with the provided password.
6. Mark invitation `accepted_at`.
7. Issue a session (same as login).

### 11.7 User removal and anonymization (ADR 065, PRD §4.2, §20.2)

Removal by Owner:
- Set `deleted_at = now()`, clear `email`, `name`, `password_hash`.
- Delete all `sessions` rows for the user.
- `UPDATE tasks SET assignee_id = NULL WHERE assignee_id = :user_id`.
- Audit log entry (`workspace.user.removed`).

Account self-deletion follows the same path, triggered by the user.

---

## 12. Security

### 12.1 Security headers (ADR 083)

Set by nginx on every response. See ADR 083 for the exact policy. Notable properties:

- Strict CSP, no `'unsafe-inline'` or `'unsafe-eval'`.
- `frame-ancestors 'none'` — clickjacking defense.
- HSTS with preload.
- `Referrer-Policy: strict-origin-when-cross-origin`.

### 12.2 Input handling

- Every request body is a Pydantic model — unknown fields rejected, types strictly checked, bounds enforced.
- Markdown user input is rendered through `rehype-sanitize` with a strict allowlist (ADR 060).
- Search strings are passed through `websearch_to_tsquery` so malformed input becomes an empty match, not a SQL error.
- All database access is parameterized via SQLAlchemy — no string-concatenated SQL.

### 12.3 Rate limiting (ADR 052)

`slowapi` decorators on sensitive endpoints. In-memory counters acceptable while production is a single instance. 429 responses follow the Decision 043 envelope with `code: "RATE_LIMITED"` and a `Retry-After` header.

### 12.4 Audit logging (ADR 084)

Append-only `audit_log` table capturing auth-sensitive events (login success/failure, role change, user removal, account deletion, invitation sent/accepted, password reset). Populated synchronously within the triggering mutation's transaction so it cannot diverge from the mutation's outcome.

### 12.5 Encryption (ADR 085)

- **In transit**: TLS 1.3 via Let's Encrypt. HSTS preload.
- **At rest**: EBS default encryption (AWS-managed KMS key); S3 SSE-S3 on the backup bucket.
- **Passwords**: Argon2id hashes only; plaintext never logged.

### 12.6 Dependency hygiene (ADR 086)

Dependabot + CodeQL + Secret Scanning on the repo. A weekly triage cadence reviews advisories; patches are merged as PRs.

---

## 13. Observability

### 13.1 Logs (ADR 075)

- FastAPI configures `structlog` for structured JSON to stdout.
- Each log line carries: `ts`, `level`, `event`, `request_id`, `user_id?`, `workspace_id?`, `path?`, `method?`, `status?`, `duration_ms?`, `exception?` (type and stack when present).
- Docker's `awslogs` log driver ships stdout/stderr to CloudWatch Logs groups:
  - `/taskflow/prod/api`
  - `/taskflow/prod/web`
  - `/taskflow/prod/db`
- Retention: 30 days.
- PII never logged — emails, names, and Markdown bodies are scrubbed or omitted.

### 13.2 Metrics

- **Host**: CloudWatch Agent reports `mem_used_percent`, `disk_used_percent`, `cpu_usage_active`, `cpu_usage_iowait` from the EC2.
- **Application**: CloudWatch Logs metric filters extract counters from structured logs:
  - `5xx_count` — count of responses with `status >= 500`.
  - `4xx_count` — count of `status` in `[400, 500)`.
  - `error_count` — count of lines with `level = "ERROR"`.
  - `login_failure_count` — count of `event = "auth.login.failure"`.
  - `websocket_connections` — gauge emitted periodically by the API.

### 13.3 Alarms (ADR 077)

Routed through the `taskflow-alerts` SNS topic (email subscription):

| Alarm | Threshold |
|-------|-----------|
| `StatusCheckFailed` (EC2) | ≥ 1 for 2 min |
| `error_count` | ≥ 5 in 5 min |
| `5xx_count` | ≥ 10 in 5 min |
| `mem_used_percent` | ≥ 85% for 10 min |
| `disk_used_percent` | ≥ 80% for 10 min |
| `login_failure_count` | ≥ 50 in 5 min (brute-force signal) |

### 13.4 Health check

`GET /health` returns 200 if the API can reach Postgres (`SELECT 1`), otherwise 503. Nginx is configured with an `upstream` health check. A CloudWatch Synthetics canary (if provisioned) hits `/health` every 5 minutes.

---

## 14. CI/CD and Deployment

### 14.1 CI (ADR 071, 082)

`.github/workflows/ci.yml` runs on every PR:

| Job | Steps |
|-----|-------|
| `lint` | `pnpm biome ci`; `ruff check`; `ruff format --check` |
| `typecheck` | `pnpm tsc -b`; `mypy apps/api/taskflow` |
| `test-frontend` | `pnpm vitest run` |
| `test-backend` | `pytest` against an ephemeral Postgres service container |
| `e2e` | Docker Compose up, Playwright smoke suite, axe checks |
| `build-images` | `docker buildx build --platform linux/arm64` (no push) — confirms Dockerfiles build |
| `openapi-drift` | Regenerate `api-types/schema.d.ts`, fail if committed copy differs |

### 14.2 CD (ADR 071, 087)

`.github/workflows/deploy.yml` runs on push to `main`:

1. Assume `taskflow-deploy-role` in AWS via GitHub OIDC (no long-lived keys).
2. Build multi-arch images (`linux/arm64`), tag with the commit SHA, push to ECR.
3. Run `aws cloudformation deploy` for each stack whose template changed.
4. Run migrations: `aws ssm send-command` to the EC2 instance, executing `docker compose run --rm api alembic upgrade head`.
5. Roll the service: `aws ssm send-command` executing `docker compose pull && docker compose up -d --remove-orphans`. Docker Compose performs a rolling update on each service — nginx stays up while `api` and `web` containers are replaced.
6. Smoke-check `/health` from the deploy workflow; fail the deploy if it doesn't return 200 within a timeout.

### 14.3 Secrets flow (ADR 073)

```
GitHub Repo Secrets (CI-level)
  └── OIDC ── AWS STS ── taskflow-deploy-role ── ECR push, CFN deploy, SSM

EC2 Instance IAM Role (runtime)
  └── SSM Parameter Store (/taskflow/prod/*) ── read at boot ── exported as env vars
```

No AWS access keys exist anywhere in source, the CI system, or the EC2 host.

### 14.4 Rollback

- **Image-level rollback**: the previous image tag is still in ECR. `docker compose up -d` with the prior `image: taskflow/api:<prior-sha>` tag restores it.
- **Schema rollback**: Alembic `downgrade` exists but is not run in production. Roll forward with a corrective migration instead.
- **Infrastructure rollback**: CloudFormation tracks changesets; `aws cloudformation cancel-update-stack` reverts in-progress stack updates.

---

## 15. Local Development

### 15.1 One-command start (ADR 039)

```
git clone taskflow && cd taskflow
cp .env.example .env.local
make dev
```

`make dev` runs `docker compose up`, which starts:

| Service | Notes |
|---------|-------|
| `api` | FastAPI + `uvicorn --reload`, source bind-mounted for hot reload |
| `web` | Vite dev server with HMR, source bind-mounted |
| `db` | PostgreSQL 16 with a named volume for persistence across restarts |
| `mailhog` | SMTP sink on `:1025`, web UI on `:8025` — stands in for SES |

### 15.2 Makefile targets

| Target | Purpose |
|--------|---------|
| `make dev` | `docker compose up` |
| `make down` | Stop and remove containers |
| `make migrate` | Run Alembic `upgrade head` |
| `make revision m="..."` | Create a new migration |
| `make seed` | Load seed data (ADR 066) |
| `make test` | Run all tests |
| `make e2e` | Run Playwright smoke suite |
| `make lint` | Biome + Ruff |
| `make typecheck` | `tsc -b` + `mypy` |
| `make build` | Production-build both images locally |

### 15.3 Seed data (ADR 066)

`make seed` runs the idempotent Python seed script. Creates "Aurora Studio" workspace with:

- 5 users covering Owner/Admin/Member/Viewer — credentials documented in the README.
- 3 projects with varied access assignments.
- ~30 tasks exercising every status, priority, label combination, and due-date state.
- Sample comments with @mentions driving notifications and activity.

---

## 16. Testing Strategy

### 16.1 Unit tests (ADR 079)

**Frontend (Vitest + React Testing Library):**
- Component rendering and interaction for UI primitives and domain components.
- Hooks (`useQuery` wrappers, form schemas).
- Permission derivations (given role + project access, what actions are allowed).

**Backend (pytest):**
- Pure service functions (permission derivations, notification fan-out rules, activity event construction).
- Pydantic schema validators.

### 16.2 Integration tests (ADR 079)

Backend integration tests bring up a real Postgres via `docker-compose.test.yml` (or `pytest-postgresql`). Each test runs inside an outer transaction that is rolled back at the end via a pytest fixture.

Coverage focus:
- Every API endpoint for each role × project-access combination.
- `LISTEN/NOTIFY` round-trip: publish an event, assert a subscribed consumer receives it.
- FTS: insert tasks, assert `websearch_to_tsquery` matches the expected subset.
- Migrations: a test boots from empty and runs `upgrade head`, then asserts schema invariants.

### 16.3 End-to-end tests (ADR 080)

Playwright smoke journeys against a seeded `docker compose up` stack:

1. Sign-up → create workspace → create first project (Owner).
2. Accept invitation (new user).
3. Create task → drag to In Progress → add comment with @mention → mark Done.
4. **Real-time cross-user** — two browser contexts; user A moves a task, user B sees the move without refresh.
5. **Notification delivery** — user A @mentions user B; user B's badge increments in real time.
6. Search, filter, empty states.

### 16.4 Accessibility tests (ADR 081)

- `@axe-core/playwright` runs on every page the E2E suite visits. Violations fail the test.
- `vitest-axe` in component tests for modals, forms, menus, the task detail panel, and the board drag-and-drop region.
- A manual keyboard-and-screen-reader pass is run at release checkpoints.

---

## 17. Performance Considerations

### 17.1 Hot paths

- **Board view load** — a single query joins `tasks`, `assignee`, `labels`, and comment counts for a project. Indexed on `(project_id, status, created_at DESC)`; result is paginated per column (first 50 tasks per status shown by default).
- **Notifications badge** — partial index `(recipient_id) WHERE read_at IS NULL` makes the unread count a single index scan.
- **Dashboard "My tasks"** — indexed `(assignee_id, due_date)` satisfies the sort without sorting at query time.
- **Search** — GIN index on `search_vector`, ranked with `ts_rank_cd`; Postgres handles the thousands-of-tasks scale comfortably.
- **Activity feed** — indexed `(workspace_id, created_at DESC)` and `(project_id, created_at DESC)`; cursor pagination by `created_at DESC, id` tiebreak.

### 17.2 Connection limits

With 2 Uvicorn workers and a default Postgres `max_connections` of 100, we size the SQLAlchemy pool conservatively at `pool_size=5, max_overflow=5` per worker — 20 connections total, well under the limit, leaving room for migrations and seeds.

### 17.3 WebSocket load

At demo scale a handful of active users rarely exceed 10 concurrent WebSocket connections. Each is a single coroutine in Uvicorn; memory per connection is small (≈50 KB). Well within the 2 GB budget.

---

## 18. Trade-offs and Known Risks

### 18.1 Trade-offs accepted for the demo scope

| Trade-off | Benefit | Cost |
|-----------|---------|------|
| Postgres on the app EC2 (no RDS) — ADR 033 | Zero managed-DB cost | Manual backup/restore; shared memory; no automatic failover |
| Single EC2 instance — ADR 036 | Lowest operational surface | No horizontal scaling; planned downtime on upgrades; single point of failure |
| In-memory rate limiting — ADR 052 | No Redis | Counters reset on restart; won't work across instances |
| Postgres-only cache/session store — ADR 068 | No Redis | Slightly higher session-lookup latency; Postgres bears all load |
| `SameSite=Lax` + double-submit CSRF — ADR 051 | No server-side CSRF store | Slightly larger cookie payload; trust in the client to echo correctly |
| Last-write-wins conflict resolution — ADR 008 | No OT / CRDT machinery | Rare edit losses under concurrent edits; real-time masks most of it |
| No third-party observability — ADR 075–077 | No vendor, no extra secret | Less ergonomic error analysis; no breadcrumbs or session replay |
| Cross-language stack (TS + Python) — ADRs 027, 028 | Use FastAPI as requested | Duplicate validation (Pydantic vs. Zod); OpenAPI codegen mitigates type drift but not behavior drift |
| Conservative optimistic UI (drag only) — ADR 046 | Simpler reconciliation | Other mutations show a brief loading state |
| SPA, no SSR — ADR 030 | Simple Python-only backend | Slightly slower time-to-first-interactive on cold loads |

### 18.2 Known risks

- **Host failure = downtime.** A hardware fault on the EC2 instance produces an outage until CloudFormation replaces it. RTO ~1h. Acceptable for a demo; documented in §5.
- **Cookie-auth + WebSocket** requires careful CSRF handling on the upgrade; tested in CI.
- **APScheduler in-process** means a restart drops in-flight scheduled-job state. The specific jobs we run are idempotent and low-stakes; a missed run is visible at the next tick.
- **Pydantic ↔ Zod drift** can cause the client to accept input the server rejects. Integration tests cover validation on critical fields (email, password rules, task title length); review discipline covers the rest.

---

## 19. Future Evolution

Architecturally, the following changes are already possible without reshaping the system:

| Future need | Path |
|-------------|------|
| Add a locale (e.g., French) | Ship a new `locales/fr.json`; no code change (ADR 018, 061) |
| Support RTL | Flip `html[dir="rtl"]`; logical properties already in use (ADR 019) |
| Public API | Package the existing `/api/v1/` with auth-key support and documentation (ADR 013, 041) |
| Dark mode | Swap token values in a new `:root[data-theme="dark"]` block (ADR 022) |
| External integrations | The service layer's event emission already exists for real-time; add webhook subscribers (ADR 012, 070) |
| Horizontal scaling | Move Postgres to RDS; add a second EC2 behind an ALB; `broadcaster` + `LISTEN/NOTIFY` already handles multi-node fan-out (ADR 045) |
| Self-hosted distribution | Single-tenant architecture and containerized deployment translate directly (ADR 003) |

### 19.1 Deliberate future ADRs

The following are out of scope for v1 but will become real ADRs when addressed:

- OpenTelemetry tracing
- Feature flags
- Email notifications (separate from in-app)
- Calendar view
- File attachments
- Custom workflows
- Offline support

---

## 20. Reference Documents

| Document | Location |
|----------|----------|
| Architectural Decision Records | [decisions/INDEX.md](decisions/INDEX.md) |
| Business Requirements Document | [../business/business-requirements-document.md](../business/business-requirements-document.md) |
| Product Requirements Document | [../product/product-requirements-document.md](../product/product-requirements-document.md) |
| Design Requirements Document | [../design/design-requirements-document.md](../design/design-requirements-document.md) |
| Business Decision Records | [../business/decisions/INDEX.md](../business/decisions/INDEX.md) |
| Product Decision Records | [../product/decisions/INDEX.md](../product/decisions/INDEX.md) |
| Design Decision Records | [../design/decisions/INDEX.md](../design/decisions/INDEX.md) |
