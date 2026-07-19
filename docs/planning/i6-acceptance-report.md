# TaskFlow — Phase I6 Acceptance Report

**Date:** 2026-07-19
**Scope:** Final acceptance against the local `docker compose` stack (seeded "Aurora Studio" workspace), per the 2026-07-19 reframing of Phase I6 (I4/I5 permanently out of scope — demonstration project, no production deployment).
**Status:** PRD walkthrough, DRD page-spec walkthrough, and empty-state verification **complete**. Findings listed in §5; No items recommended for follow-up.

---

## 1. Verification Baseline

All three automated suites were run against the live stack on the acceptance date:

| Suite | Result |
|-------|--------|
| Backend integration + unit (`docker-compose.test.yml`) | **268 passed** (27s) |
| Web component tests (`pnpm --filter @taskflow/web test -- --coverage`) | **195 passed**; coverage 94.6% statements / 82.7% branches |
| Playwright E2E (6 journeys, seeded stack) | **6/6 green, twice consecutively** — after the Journey 3 fix below |

Journey 3's tracked cold-stack drag flake recurred and was fixed per the 2026-07-18 note's instruction: `e2e/helpers/dnd.ts` now pauses 150 ms after crossing the dnd-kit activation threshold and again before releasing, so collision detection registers the drop target. Suite went green twice consecutively afterward.

## 2. PRD Walkthrough (section → evidence)

Method: every PRD section was verified against the running stack via a scripted browser walkthrough (29 screenshots: owner, viewer, and fresh-workspace contexts at desktop/tablet/mobile viewports), backed by the green automated suites for behaviors already covered there.

| PRD § | Area | Evidence | Verdict |
|-------|------|----------|---------|
| 2, 2.1 | Roles & permission matrix | B3 unit tests cover every role × action × access cell; role sweeps in integration tests; viewer UI gating confirmed visually (no Create task / settings gear / sidebar `+`; only accessible projects listed) | Pass |
| 3.1–3.2 | Sign up / log in | Journey 1; signup & login screens visually match; login lands on dashboard | Pass |
| 3.3 | Invitations | Journey 2 (MailHog token recovery → accept); invitation preview endpoint drives workspace/role/inviter display; pending/accepted status visible in Members tab | Pass |
| 3.4 | First-run | Fresh-workspace capture shows "Create your first project" + sidebar "Invite team members"; invited-user welcome covered by H2 tests | Pass |
| 3.5 | Empty states | See §4 below | Pass |
| 4 | Workspace & member management | C1 integration tests (role change, removal anonymization + unassignment); Members tab visual | Pass |
| 5 | Projects & access | C2 integration tests incl. cross-workspace isolation; viewer sidebar correctly omits inaccessible project | Pass |
| 6 | Tasks (fields, statuses, due dates, priority, ordering, cancelled) | C3 integration tests; board/list/panel visuals show priority icons, overdue styling, cancelled hidden by default | Pass |
| 7 | Labels | C1 tests; Labels tab + palette chips verified visually | Pass |
| 8 | Board view | Board visuals (columns, counts, cards, meta row); drag-drop via Journey 3; column highlight per G3 tests | Pass |
| 9 | List view | List visuals; inline status dropdown per G4 tests; shared filter state via URL | Pass, with known deviation (F3) |
| 10 | Task detail panel | Deep link opened the panel over the last-used view (PRD §9.3 confirmed in passing); properties, Markdown description, comments all present; viewer read-only per G5 tests | Pass |
| 11 | Comments & @mentions | Journey 3; mention chips render teal in comment bodies; author-only edit/delete per ADR 088 tests | Pass |
| 12 | Search & filters | Journey 6; search dropdown with highlighted match + status badge; filter chips + clear-all verified visually | Pass |
| 13 | Dashboard | My Tasks / Recent Activity / Projects sections visually verified | Pass, with content gap (F1) |
| 14 | Activity feeds | Workspace feed on dashboard; project-scope side panel (Open Item #4 deliverable) verified visually | Pass, with content gap (F1) |
| 15 | Notifications | C6 integration tests (all four triggers + self-suppression); Journey 5 (real-time badge); page + empty state visual | Pass |
| 16 | Accessibility | vitest-axe across component suite; @axe-core/playwright in journeys; manual passes remain open (§6) | Pass (automated scope) |
| 17 | Responsive | Tablet icon rail, mobile hamburger + stacked board columns, mobile full-screen task panel all verified visually | Pass, with cosmetic deviation (F2) |
| 18 | i18n | `react-intl` + externalized `en.json`; logical CSS properties enforced | Pass |
| 19 | Real-time | Journeys 4 & 5 (cross-user move, live badge) | Pass |
| 20 | Profile & account deletion | Profile tab visual (name save, change password, danger zone); B4 tests for change-password session revocation + delete anonymization | Pass |

## 3. DRD Page-Spec Walkthrough

Screens captured and reviewed against DRD §8–§11 (screenshots archived in the session scratchpad; not committed):

- **Login / Sign up (§8.1)** — centered 400px card, logo + wordmark, correct headings/subtext, teal primary, footer links. Match.
- **Password reset request** — same card pattern, "Reset your password". Match.
- **Dashboard (§8.3)** — 60/40 grid, grouped My Tasks rows (priority icon / title / status badge / due date), sentence-style activity with avatars + relative timestamps, project rows with color dots + status counts. Match (see F1 for activity copy).
- **Board (§8.4)** — sub-nav (Board/List toggle with teal active state, Filter, Sort, history + settings icons, Create task), filter chip bar with × dismiss + "Clear all", 5 columns with status dots + counts, cards with labels (chips), meta row, 24px avatars. Cancelled hidden. Match.
- **List (§8.5)** — all six columns, status text styling, priority icon + label, overdue dates red, label chips. Match (F3: title/status header sort not offered — previously reconciled in G4).
- **Task detail panel (§9.1)** — header with inline-editable title + close, properties grid (status badge, assignee, priority, due date, labels), rendered Markdown description, chronological comments with teal @mention chips, comment composer. Match.
- **Notifications (§8.6)** — page + "You're all caught up." empty state. Match.
- **Settings (§8.7–§8.10)** — horizontal tabs; Workspace name+Save; Members (role dropdowns, Owner row locked, remove buttons, pending invitations with status); Labels (swatch chips, edit/delete, Create label); Profile (avatar + read-only email, display name save, change password, danger zone). Match.
- **Modals (§10.1)** — Create Project modal (name required, description textarea, Cancel/Create footer, dimmed backdrop). Match. Other modals covered by G8/H3 component tests with exact DRD copy.
- **Search overlay (§11.1)** — dropdown under input, matched-text highlight, project + status badge per result, "No tasks match your search." empty state. Match.
- **Project activity panel (PRD §14.2)** — slide-in panel from the sub-nav History icon, project-scoped entries. Match (F1 applies).
- **Responsive (§15)** — tablet: icon-only sidebar rail, fixed-width columns with horizontal scroll; mobile: hamburger header, stacked full-width board columns, full-screen task panel. Match (F2: dashboard mobile section order).

## 4. Empty States (DRD §16 / PRD §3.5)

| Area | Expected copy | Verified |
|------|---------------|----------|
| Dashboard — My Tasks | "No tasks assigned to you yet." + browse link | ✔ visual (fresh workspace) |
| Dashboard — Recent Activity | "No recent activity." | ✔ visual |
| Dashboard — Projects | "No projects yet." + Create button (role-aware) | ✔ visual; viewer no-button variant per H2 tests |
| Board (no tasks) | "This project has no tasks yet." + Create a task | ✔ visual (fresh project) |
| Empty status column | Subtle "No tasks" hint | ✔ `BoardView.tsx` + H2 component tests |
| Search — no results | "No tasks match your search." | ✔ visual |
| Filter — no results | "No tasks match these filters." + Clear filters | ✔ visual |
| Notifications | "You're all caught up." | ✔ visual |
| First-run (Owner) | Create-first-project prompt + sidebar invite prompt | ✔ visual |
| First-run (invited) | Workspace-named welcome | ✔ H2 component tests |

## 5. Findings

- **F1 — Activity entries omit the task name for status-change and comment events.** Feed copy reads "moved a task to in_progress" / "commented on a task": the task is not named (PRD §13.2: each entry shows *which task*; DRD §8.3: task names teal and clickable — satisfied only for `task.created` entries), and the raw status key (`in_progress`) appears instead of the display label ("In Progress"). Affects the dashboard feed and the project activity panel.
- **F2 — Mobile dashboard section order.** Stacks My Tasks → Recent Activity → Projects; DRD §15.3 specifies My Tasks → Projects → Recent Activity. Cosmetic.
- **F3 — List view title/status header sort not offered.** Pre-existing, documented deviation (status file G4 note): sort is offered on the backend-supported keys (priority, due date, assignee) only; PRD §9.1 says all columns sortable.
- **F4 — Seeded workspace accumulates E2E artifacts.** Journeys create `E2E realtime <ts>` / `E2E lifecycle <ts>` tasks and invitees in Aurora Studio (by design — the suite reruns against a persisted DB). Before recording videos: `docker compose down -v && make e2e-up` for a pristine seed.
- **F5 — `make test` clobbers the running dev database container.** `docker-compose.test.yml` redefines `db` (tmpfs, `taskflow_test`) under the same compose project, so running backend tests while the dev stack is up replaces the dev `db` container and the API starts failing with `database "taskflow" does not exist`. Recovery: `docker compose up -d db && docker compose restart api` (the named volume survives). Fix candidate: give the test stack its own project name (e.g. `docker compose -p taskflow-test -f docker-compose.test.yml …`).

## 6. Carried-Over Loose Ends — Disposition

- **Manual a11y checklist (`apps/web/docs/a11y-manual-checklist.md`):** requires a human at the machine (VoiceOver, keyboard-only journey, contrast spot checks) — cannot be closed by automation. Remains open as the documented manual pass; automated coverage (vitest-axe + @axe-core/playwright) is green.

## 7. Remaining I6 Items

Completed 2026-07-19, after this report's walkthroughs: README updated (run/seed refreshed, deployment section added as reference-only), release note authored ([release-note.md](./release-note.md)), status file marked complete.
