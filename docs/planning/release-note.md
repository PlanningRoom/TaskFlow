# TaskFlow v1.0 — Release Note

**Date:** 2026-07-19
**Verdict:** All in-scope phases of the [implementation plan](./implementation-plan.md) are complete (40 of 40; the two production-cutover phases were permanently descoped — TaskFlow is a demonstration project and runs locally). Final acceptance: [i6-acceptance-report.md](./i6-acceptance-report.md).

## What shipped

TaskFlow is a collaborative task-management web app for small teams: one workspace per user, four roles (Owner / Admin / Member / Viewer), projects with per-user access control, and tasks that flow through a fixed six-status workflow.

**For users:**

- **Auth & onboarding** — email/password signup that creates a workspace, login, password reset by email, invitation flow with a preview screen (workspace, inviter, role) and new-vs-existing-account branching, role-aware first-run prompts and empty states throughout.
- **Projects & tasks** — project CRUD with access management; tasks with Markdown descriptions, assignee, priority, due dates (overdue/approaching styling), and workspace-wide colored labels; cancelled tasks hidden by default.
- **Three ways to work** — drag-and-drop board (desktop), sortable list view, and a slide-in task detail panel with inline editing, deep links, and @mention autocomplete in comments. Filter and sort state lives in the URL and is shared between views; last-used view per project is remembered.
- **Collaboration in real time** — WebSocket fan-out updates boards, the task panel, notifications, and activity feeds across users without refresh; optimistic status changes with rollback on error.
- **Notifications** — four triggers (mention, assignment, status change on your task, comment on your task) with self-trigger suppression, a live unread badge, and a mark-all-read page.
- **Search & dashboards** — ⌘K full-text search across accessible projects; a dashboard with My Tasks (grouped, overdue-first), workspace activity, and per-project status counts; a project-scoped activity panel.
- **Accessibility & responsive** — WCAG 2.1 AA-targeted: keyboard-operable throughout, list view as the DnD alternative, axe checks on every component; desktop / tablet icon-rail / mobile layouts.

**Under the hood:**

- FastAPI + async SQLAlchemy + Postgres (UUIDv7 keys, generated FTS column), Alembic migrations on boot, Argon2id sessions in Postgres, CSRF double-submit, rate limiting, structured PII-scrubbed logging, synchronous audit log, APScheduler background jobs, and email via SMTP/MailHog in dev (Resend adapter for prod).
- React 19 + Vite + TanStack Query/Router, Radix primitives themed by DRD design tokens, types generated from OpenAPI with a CI drift gate.
- Verification: 268 backend tests (~98% coverage on services/auth), 195 web component tests (94%+ statements), 6 Playwright journeys against the real compose stack, all green in CI alongside lint/typecheck/cfn-lint/build-images gates.

## Known limitations

By design (PRD §21): no file attachments, subtasks, bulk operations, custom workflows, email notifications, calendar view, integrations, or public API. Accepted minor deviations are recorded as findings F1–F5 in the [acceptance report](./i6-acceptance-report.md) (notably: activity-feed entries don't name the task for status-change/comment events, and the mobile dashboard section order differs from DRD §15.3).

## Running it

See the [README](../../README.md): `make dev` + `make seed`, then log in as `owner@aurora.example.com` / `correct-horse-battery-staple`. Deployment artifacts (CloudFormation, CD pipeline, runbook) are reference-only — nothing is deployed.
