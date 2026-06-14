# TaskFlow — Readiness Test Plan (through Phase H5 — Part H complete)

**Version:** 4.0
**Date:** 2026-06-14
**Scope:** Manual UI testing of everything built **through Phase H5** — all of Part G (Frontend Screens) plus Part H (Cross-Cutting: real-time, empty states/first-run, toasts/errors, accessibility, test completion).
**Audience:** Whoever is clicking through the running app to confirm it behaves.

---

## 1. What this covers

Parts G **and H** are complete: every screen behind the shell is real, backend-wired UI, and the cross-cutting layer is in place. You can authenticate (G1), land on a real dashboard (G2), open a project's **board** and **list** views (G3/G4), open the **task detail panel** to edit properties and comment (G5), read **notifications** (G6), use global **search** (G7), and manage **settings** (G8). On top of that, changes now **stream live across tabs and users** (H1), every async action gives **toast feedback** with standardized error messaging (H3), and **first-run prompts/empty states** are complete and role-aware (H2).

This plan tests, in order:

1. **Auth screens (G1)** — Login, Sign Up, Accept Invitation, Password Reset.
2. **App shell + routing (F4)** — sidebar, header, breadcrumb, responsive behavior.
3. **Dashboard (G2)** — My Tasks, Recent Activity, Projects, empty/first-run states, Create Project modal.
4. **Board (G3)** — columns, cards, drag-and-drop status, filters, sort, Create Task modal, Project Settings modal.
5. **List (G4)** — sortable table, inline status, shared filter/sort with the board.
6. **Task Detail panel (G5)** — inline property editors, Markdown description, comments + @mentions.
7. **Notifications (G6)** — list, mark-as-read, header bell badge.
8. **Search (G7)** — ⌘K overlay, ranked results, keyboard navigation.
9. **Settings (G8)** — Workspace, Members, Labels, Profile, with role-gated access.
10. **Real-time (H1)** — live cross-tab/user updates for boards, tasks, comments, notifications, activity (new §19).

### What's new since v3.0 (G8)

- **Real-time updates (H1) are live.** Boards, the task panel, notifications, and activity update **without a refresh** when something changes in another tab or by another user. A discreet "Reconnecting…" pill shows if the socket drops. The "refresh to see changes" caveats from v3.0 are **gone** — see new §19.
- **Toasts & error feedback (H3).** Success toasts confirm saves; a **standardized error toast** ("Couldn't save your changes. Please try again.") now appears when an action fails (e.g. a drag-and-drop whose save is rejected, a role change, a remove/delete). Toasts auto-dismiss after ~5s and can be **manually dismissed** (× on the toast).
- **First-run & empty states (H2).** The Owner now also sees an **"Invite team members"** prompt in the sidebar until the first invitation is sent; the invited-user welcome **names the workspace** ("Welcome to Aurora Studio."); the empty **My Tasks** state offers a "Browse projects" link.
- **Accessibility (H4)** has had an automated `vitest-axe` pass across components; a manual VoiceOver/contrast checklist lives at `apps/web/docs/a11y-manual-checklist.md`.

### Out of scope (not built yet — don't file these as bugs)

- **Responsive/mobile polish** — tablet icon-rail, mobile hamburger, board column stacking, and list mobile layout are **deferred** (DRD §15 / F4 note). Below `md` the sidebar is hidden; wide screens are the test target.
- **@mention rendering** — posted comments show the raw `@handle` text rather than a teal-styled chip; autocomplete insertion and backend resolution/notification *are* wired. (Tracked refinement.)
- **List header sort** is offered only for backend-supported keys (priority / due / assignee); **Title and Status columns are not click-to-sort**.
- **Manual accessibility passes** — keyboard sweep, screen-reader (VoiceOver), and color-contrast spot-checks are the standing pre-launch checklist (`apps/web/docs/a11y-manual-checklist.md`); §20 here is the lightweight version, not the full WCAG audit.

> If something matches a deferred item above, note it under "Observations," not "Defects."

---

## 2. Environment setup

Pick one. Option A is closest to production; Option B gives faster reloads if you'll iterate.

### Option A — Full Docker stack (recommended for a first look)

```bash
make dev      # boots db + mailhog + api + web
make seed     # in a second terminal: loads the Aurora Studio demo data
```

- **App:** http://localhost:5173
- **MailHog inbox** (catches password-reset & invitation emails): http://localhost:8025
- **API health:** http://localhost:8000/health → should return `200`

### Option B — Backend in Docker, frontend native

```bash
docker compose up db mailhog api     # backend only
make seed                            # load demo data (second terminal)
cd apps/web && pnpm dev              # Vite native
```

Vite proxies `/api` and `/ws` to `localhost:8000`, so cookies flow same-origin with no CORS setup.

> **Known gotcha (this machine):** the Docker `web` container fails to install over the bind mount — use **Option B** (backend in Docker, Vite on host). See `docs/technical/local-dev-startup.md`.

### Pre-flight checks (do these before any test below)

- [ ] http://localhost:8000/health returns `200`
- [ ] http://localhost:5173 loads without a blank page or console errors
- [ ] `make seed` completed without error (re-running is a safe no-op)
- [ ] MailHog UI loads at http://localhost:8025

---

## 3. Seed credentials

`make seed` creates the **Aurora Studio** workspace. Password for **all** users: `correct-horse-battery-staple`

| Email | Display name | Role |
|-------|--------------|------|
| `owner@aurora.example.com` | Aurora Owens | Owner |
| `admin@aurora.example.com` | Adam Min | Admin |
| `dev1@aurora.example.com` | Dana Engineer | Member |
| `dev2@aurora.example.com` | Mason Code | Member |
| `viewer@aurora.example.com` | Vivian Watch | Viewer |

> Note: each user belongs to exactly one workspace. Signing up creates a *brand-new* workspace with you as Owner — it does **not** join Aurora Studio. To join Aurora Studio you'd need an invitation.

### Seed shape that matters for the screens

The seed builds **3 projects** with this access layout (Owner + Admin have implicit access to all):

| Project | Color dot | Members with explicit access |
|---------|-----------|------------------------------|
| Mobile App Redesign | purple | dev1, dev2, viewer |
| API Migration | blue | dev1 |
| Marketing Site | green | viewer |

**Tasks:** ~30 across every status, priority, label, and due-date state (overdue / today / this week / future / none). Cancelled tasks exist but are hidden by default. **Assignments** go to **dev1** and **dev2** only. **Comments** with **@mentions** are seeded, so activity, mentions, and notifications have data.

- **dev1 / dev2** → populated "My Tasks," assigned cards, mention/assignment notifications.
- Use **Mobile App Redesign** as the richest project (3 members, most tasks).

---

## 4. How to use this plan

- Work top-to-bottom; later sections assume earlier ones passed.
- Each test has a **Steps** list and an **Expected** result. Tick the checkbox if it matches.
- Use a **fresh browser profile or incognito window** per auth journey so stale cookies don't mask bugs. Keep **DevTools → Application → Cookies** and the **Console** tab open throughout.
- Log anything that fails in §22 (Defect Log).

**Reference specs** if you need to settle "is this a bug?":
DRD §8.1 (Login/Signup), §8.2 (Accept Invitation), §8.3 (Dashboard), §8.4 (Board), §8.5 (List), §8.6 (Notifications), §8.7–§8.10 (Settings), §9 (Task panel), §10 (modals), §11.1 (Search), §11.4 (@mention), §16 (Empty states), §18 (Validation/confirmations) · PRD §3 (Auth), §6 (Tasks), §8 (Board), §9 (List), §10 (Task detail), §11 (Comments), §12 (Search), §13 (Dashboard), §15 (Notifications), §4/§7/§20 (Settings) · TDD §11 (Sessions/cookies).

---

## 5. App shell & routing (Phase F4)

Test these while logged in as **Owner** (log in first via §6 if needed).

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 5.1 | Shell renders | Log in, observe layout | Sidebar (240px, left) + header (52px, top) + content area | [ ] |
| 5.2 | Sidebar nav | Inspect sidebar | Logo block; Dashboard + Notifications links; Projects section; bottom Settings link + user identity block | [ ] |
| 5.3 | Header | Inspect header | Breadcrumb, search input (⌘K hint), notification bell, user avatar | [ ] |
| 5.3b | User menu | Click the header avatar | A dropdown opens (DRD §11.2): display name, email, role badge, **Settings** link, **Sign out** action | [ ] |
| 5.4 | Active nav state | Click Dashboard, then Notifications | The current route's nav item is visually highlighted | [ ] |
| 5.5 | Breadcrumb updates | Navigate between routes | Breadcrumb reflects current route | [ ] |
| 5.6 | Bare project URL redirect | Visit `/projects/<any-id>` directly | Redirects to `…/board` (or your last-used view for that project) | [ ] |
| 5.7 | Routes load | Visit `/notifications`, `/settings/profile`, a project board | Each loads inside the shell without crashing — now real content (§13–§18) | [ ] |
| 5.8 | Responsive (desktop) | Window ≥ `md` width | Sidebar visible alongside content | [ ] |
| 5.9 | Responsive (narrow) | Shrink below `md` | Sidebar hides cleanly; content reflows (icon-rail/hamburger polish is deferred — not a bug) | [ ] |
| 5.10 | Unauth routes are shell-free | Log out, visit `/login`, `/signup` | Rendered as centered cards, NOT inside the sidebar/header shell | [ ] |

---

## 6. Login (DRD §8.1, PRD §3.2)

Use an incognito window. Start at http://localhost:5173 — unauthenticated, you should be routed to `/login`.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 6.1 | Layout | Observe `/login` | Centered card (~400px), logo above form, "Welcome back" heading, email + password fields, full-width primary button, footer link to sign up | [ ] |
| 6.2 | Happy path | Enter `owner@aurora.example.com` / `correct-horse-battery-staple`, submit | Logs in, redirects to `/dashboard` (real content — see §12) | [ ] |
| 6.3 | Session cookie set | After 6.2, DevTools → Application → Cookies | Session cookie present with `HttpOnly`, `Secure`*, `SameSite=Lax` (*Secure may be relaxed on `http://localhost` — note if so) | [ ] |
| 6.4 | Wrong password | Correct email, wrong password | Inline/error message; **no** redirect; message does NOT reveal whether the email exists | [ ] |
| 6.5 | Unknown email | `nobody@aurora.example.com` / anything | Same generic failure as 6.4 (no account enumeration) | [ ] |
| 6.6 | Empty fields | Submit blank form | Inline validation on required fields (on blur and on submit per DRD §18.1) | [ ] |
| 6.7 | Malformed email | `notanemail`, any password | Inline email-format validation before/at submit | [ ] |
| 6.8 | Link to signup | Click footer link | Navigates to `/signup` | [ ] |
| 6.9 | Already logged in | While authenticated, visit `/login` | Redirects to `/dashboard` | [ ] |
| 6.10 | Each role logs in | Repeat 6.2 for admin / dev1 / dev2 / viewer | All five succeed and land in the shell | [ ] |

---

## 7. Sign Up (DRD §8.1, PRD §3.1)

Sign-up creates a **new workspace** with you as Owner. Use a fresh incognito window.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 7.1 | Layout | Observe `/signup` | Same card shell as login; heading "Create your workspace"; footer link to login | [ ] |
| 7.2 | Happy path | Enter a new email (e.g. `tester+1@example.com`), valid password (≥ 8 chars), submit | Account created, logged in as Owner of a brand-new empty workspace, redirected into the shell | [ ] |
| 7.3 | New workspace is empty | After 7.2, look at the dashboard | No Aurora Studio data; the Owner **first-run** state shows (see §12.5) — confirms isolation (workspace-per-signup) | [ ] |
| 7.4 | Password too short | Password of < 8 chars | Inline validation; submit blocked (backend enforces min 8) | [ ] |
| 7.5 | Malformed email | `bad-email` | Inline email-format validation | [ ] |
| 7.6 | Duplicate email | Sign up again with an email already used | Graceful error, no crash, no silent overwrite | [ ] |
| 7.7 | Required fields | Submit blank | Inline validation on each required field | [ ] |
| 7.8 | Switch to login | Click footer link | Navigates to `/login` | [ ] |

> Keep the fresh workspace from 7.2 — you'll reuse it in §12.5 (first-run prompts) and §12.6 (Create Project modal from an empty state).

---

## 8. Password Reset — Request (PRD §3, TDD §11)

This flow emails a reset link, caught by **MailHog** (http://localhost:8025).

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 8.1 | Reach the screen | From `/login`, click the password-reset link | Reset-request screen with an email field | [ ] |
| 8.2 | Request for real user | Enter `dev2@aurora.example.com`, submit | Generic "if an account exists, we've sent a link" style confirmation (no-enumeration) | [ ] |
| 8.3 | Email arrives | Open MailHog | A password-reset email is present for `dev2@aurora.example.com` with a reset link | [ ] |
| 8.4 | Request for unknown email | Enter `ghost@aurora.example.com`, submit | **Same** generic confirmation as 8.2; **no** email in MailHog (no enumeration) | [ ] |
| 8.5 | Malformed email | `nope` | Inline validation before submit | [ ] |

---

## 9. Password Reset — Confirm (PRD §3, TDD §11)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 9.1 | Open valid link | Click the reset link from the 8.3 email | Reset-confirm screen with new-password field(s) | [ ] |
| 9.2 | Set new password | Enter a valid new password, submit | Success; routed to login (or auto-logged-in — note actual) | [ ] |
| 9.3 | Log in with new password | Go to `/login`, use `dev2@aurora.example.com` + the new password | Login succeeds | [ ] |
| 9.4 | Old password rejected | Try logging in with `correct-horse-battery-staple` for dev2 | Fails (password was changed) | [ ] |
| 9.5 | Token is single-use | Re-open the same reset link from 9.1 | Rejected / expired state — link cannot be reused | [ ] |
| 9.6 | Sessions revoked | If dev2 was logged in elsewhere before reset | That session is invalidated (TDD §11 — reset revokes sessions) | [ ] |
| 9.7 | Short new password | Enter < 8 chars on confirm | Inline validation; submit blocked | [ ] |

> **Reset dev2's password back** to `correct-horse-battery-staple` afterward, or re-run `make seed` against a fresh DB, so later runs use the documented credential.

---

## 10. Accept Invitation (DRD §8.2, PRD §3.3)

With **G8 built**, you can now generate invitations from **Settings → Members** (§18.3) instead of the API. For the **accept** screen itself:

> **G1 caveat (still applies):** the accept screen is a **blind accept form** — there's no backend invitation-preview endpoint yet, so workspace name / role / inviter preview, email prefill, and new-vs-existing branching are **deferred**. Tests 10.1, 10.3, and 10.5 are marked *(deferred)*.

To get a link: send an invite via §18.3 (or the API snippet below), then open MailHog → the invitation email → copy the `/invitations/<token>` link into a fresh incognito window.

```bash
# API alternative — log in as Owner, capture cookies, send an invite
curl -s -c /tmp/tf-cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"owner@aurora.example.com","password":"correct-horse-battery-staple"}'  # pragma: allowlist secret
# Read the taskflow_csrf cookie value from /tmp/tf-cookies.txt and pass it as the header:
curl -s -b /tmp/tf-cookies.txt -X POST http://localhost:8000/api/v1/workspaces/me/invitations \
  -H 'Content-Type: application/json' -H 'X-CSRF-Token: <paste csrf cookie value>' \
  -d '{"email":"newhire@example.com","role":"member"}'
```

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 10.1 | New-user accept screen *(deferred preview)* | Open the invitation link | Account-creation form (display name + password) accepts the token. Workspace/role/inviter preview and email pre-fill are **deferred** — absence is expected | [ ] |
| 10.2 | Complete new-user accept | Fill display name + password, submit | Account created, joined Aurora Studio with the invited role, logged in, lands on the dashboard | [ ] |
| 10.3 | Existing-user accept *(deferred)* | Invite an email that's already a user, open link | Should let an existing user join; branching UI is deferred — note actual behavior | [ ] |
| 10.4 | Expired/invalid token | Open `/invitations/totally-bogus-token` | Error state directing the user to ask an admin to resend (no crash) | [ ] |
| 10.5 | Email pre-fill is locked *(deferred)* | On the new-user form | Pre-fill/lock is deferred — note actual behavior | [ ] |

> Existing-user accept (10.3) **replaces** their workspace membership per PRD §3.3 — only test this with a throwaway user, or skip it.

---

## 11. Session & logout behavior (TDD §11)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 11.1 | Logout | While logged in, trigger logout (user menu in header) | Session cookie cleared; redirected to `/login` | [ ] |
| 11.2 | Protected route while logged out | After logout, visit `/dashboard` directly | Redirected to `/login` (not shown the shell) | [ ] |
| 11.3 | Refresh persists session | Log in, hard-refresh the page | Stays logged in (session cookie survives reload) | [ ] |
| 11.4 | `/auth/me` drives identity | Log in, check the header user block | Shows the correct display name / initials / avatar color for the logged-in user | [ ] |

---

## 12. Dashboard (Phase G2) — DRD §8.3, PRD §13

The dashboard is the landing screen after login at `/dashboard`. It has three sections — **My Tasks**, **Recent Activity**, **Projects** — plus role-aware empty states, first-run prompts, and the Create Project modal.

> **Real-time (H1) is on:** activity and dashboard data update live when changes happen elsewhere. If a panel ever looks stale, a refresh should never be *required* — note it as a defect if it is. Dedicated cross-tab real-time tests are in §19.

### 12.1 Layout & loading

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 12.1.1 | Two-column grid | Log in as Owner, view `/dashboard` at desktop width | Roughly 60/40 two-column layout (DRD §8.3): primary column (My Tasks / Activity) + Projects column | [ ] |
| 12.1.2 | Loading state | Throttle network (DevTools) and reload | A loading indicator/skeleton shows, not a flash of "empty" or a crash | [ ] |
| 12.1.3 | Sections present | Observe the page | "My tasks", "Recent activity", and "Projects" sections are all labeled and present | [ ] |
| 12.1.4 | Responsive reflow | Shrink the window | Columns stack vertically; nothing overflows or overlaps | [ ] |

### 12.2 My Tasks section (PRD §13.1)

> Log in as **dev1@aurora.example.com** for a populated section. Owner/Admin/Viewer correctly see this **empty** (no seeded assignments).

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 12.2.1 | Populated for dev1 | Log in as dev1, view My Tasks | Tasks assigned to dev1 appear, **grouped by project** with the project name as a group heading | [ ] |
| 12.2.2 | Task row content | Inspect a task row | Shows priority icon, title, status badge, and due date (per DRD §8.3) | [ ] |
| 12.2.3 | Ordering | Scan the order within/across groups | Overdue and soonest-due first; tasks with **no due date last** (overdue rows visually flagged) | [ ] |
| 12.2.4 | Done/cancelled excluded | Compare against the board later | Completed and cancelled tasks do **not** appear in My Tasks | [ ] |
| 12.2.5 | Empty for non-assignees | Log in as Owner (or Viewer) | My Tasks shows a friendly empty state (DRD §16); when the user has accessible projects, a **"Browse projects"** link is offered (H2) | [ ] |
| 12.2.6 | Task link target | Click a task | Opens the **task detail panel** over that project's view (G5 — see §15) | [ ] |

### 12.3 Recent Activity section (PRD §13.2)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 12.3.1 | Populated | As Owner, view Recent Activity | Sentence-style entries (avatar + who did what), most recent first | [ ] |
| 12.3.2 | Relative timestamps | Inspect entries | Times shown relative ("2 hours ago" style), not raw ISO timestamps | [ ] |
| 12.3.3 | Task links | Find an entry referencing a task | The task reference is a link (teal per DRD), clickable toward the task | [ ] |
| 12.3.4 | Access-scoped | Log in as **viewer** vs **dev1** and compare | Each user sees activity only for projects they can access (viewer: Mobile App Redesign + Marketing Site; dev1: Mobile App Redesign + API Migration) — no cross-project leakage | [ ] |
| 12.3.5 | Empty state | On a fresh signup workspace (from §7.2) | "No recent activity" empty state, not a crash | [ ] |

### 12.4 Projects section (PRD §13.3, DRD §8.3)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 12.4.1 | Owner/Admin see all 3 | Log in as Owner | All three projects appear: API Migration, Marketing Site, Mobile App Redesign (alphabetical) | [ ] |
| 12.4.2 | Project card content | Inspect a card | Color dot (purple/blue/green per §3), project name, and a status-count summary | [ ] |
| 12.4.3 | Status counts correct | Cross-check one project's counts against the board/list | Counts by status match the project's tasks | [ ] |
| 12.4.4 | Member-scoped visibility | Log in as **dev1** | Sees only **Mobile App Redesign** + **API Migration** (not Marketing Site) | [ ] |
| 12.4.5 | Member-scoped visibility (2) | Log in as **dev2** | Sees only **Mobile App Redesign** | [ ] |
| 12.4.6 | Viewer-scoped visibility | Log in as **viewer** | Sees **Mobile App Redesign** + **Marketing Site** | [ ] |
| 12.4.7 | Card navigates to project | Click a project card | Navigates to that project's board (§13) | [ ] |

### 12.5 Empty states & first-run prompts (PRD §3.4, DRD §16)

Use the **fresh workspace** you created in §7.2 (zero projects, no activity, no assignments).

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 12.5.1 | Owner first-run (project) | Log in as the fresh-signup Owner | Dashboard shows an Owner first-run state — a "Create your first project" prompt/CTA (DRD §16) | [ ] |
| 12.5.2 | No projects empty state | Look at the Projects section on the fresh workspace | A "No projects yet" empty state with a create CTA, not a blank column | [ ] |
| 12.5.3 | Empty My Tasks | Same fresh workspace | My Tasks shows its empty state | [ ] |
| 12.5.4 | Role-aware copy | Compare Owner (fresh) vs a non-owner empty view | Copy/CTA differs by capability — only roles that can create projects see the create CTA | [ ] |
| 12.5.5 | Owner first-run (invite) **(H2)** | On the fresh workspace, look at the **sidebar** (bottom, near Settings) | An **"Invite team members"** prompt is shown (it opens the Invite Member modal). It **disappears once the first invitation is sent** | [ ] |
| 12.5.6 | Invited-user welcome **(H2)** | (Optional) Accept an invite (§10.2) into Aurora as a brand-new member with no assignments | A welcome message that **names the workspace** ("Welcome to Aurora Studio.") shows until the user has an assignment/activity (PRD §3.4) | [ ] |

### 12.6 Create Project modal (DRD §10.1)

Reachable from three triggers — verify each opens the **same** modal.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 12.6.1 | Open from sidebar `+` | As Owner, click the `+` in the sidebar Projects section | Create Project modal opens (name + optional description per DRD §10.1) | [ ] |
| 12.6.2 | Open from empty state | On the fresh workspace, click the dashboard "No projects yet" / first-run CTA | The same Create Project modal opens | [ ] |
| 12.6.3 | Validation | Submit with an empty name | Inline validation; submit blocked | [ ] |
| 12.6.4 | Happy path | Enter a name, submit | Project is created; modal closes; success toast; you navigate to the new project's board; it appears in the sidebar list and dashboard Projects without a refresh | [ ] |
| 12.6.5 | Dismiss | Open the modal, press Esc / click backdrop / Cancel | Modal closes without creating a project | [ ] |
| 12.6.6 | Role gating | Log in as **viewer**, look for create entry points | Viewer does **not** get a create-project CTA or sidebar `+` (PRD §5.1 — create is Owner/Admin/Member) | [ ] |
| 12.6.7 | First-run clears | After creating the first project on the fresh workspace | The Owner "create your first project" first-run prompt no longer shows | [ ] |

---

## 13. Board View (Phase G3) — DRD §8.4, PRD §8

Open a project's board: log in as **dev1**, click **Mobile App Redesign** (richest project) from the sidebar or dashboard. URL is `/projects/<id>/board`.

### 13.1 Sub-nav & columns

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 13.1.1 | Sub-nav present | Observe the bar above the board | View toggle (Board/List, Board active), Filter button, Sort dropdown; right side: project-settings gear (Owner/Admin only) + "Create task" button (hidden for Viewer) | [ ] |
| 13.1.2 | Five columns | Look at the columns | Backlog, To Do, In Progress, In Review, Done — left to right. **Cancelled is hidden** by default | [ ] |
| 13.1.3 | Column headers | Inspect a column header | Status color dot, status name, and a task count | [ ] |
| 13.1.4 | Cards in correct columns | Spot-check a couple of tasks | Each card sits under its current status column | [ ] |
| 13.1.5 | Card content | Inspect a card | Title (up to 2 lines), up to 3 label chips (+ "+N" overflow), and a meta row: priority icon / due date / comment count / assignee avatar | [ ] |
| 13.1.6 | Overdue styling | Find a card with a past due date | Its due date is visually flagged (red) | [ ] |
| 13.1.7 | Empty column hint | Find a column with no tasks | Shows a subtle "No tasks" hint, not a blank gap | [ ] |

### 13.2 Drag-and-drop (desktop)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 13.2.1 | Drag changes status | As dev1, drag a card from To Do to In Progress | Card moves; the drop column highlights while dragging; the move sticks **immediately** (optimistic) | [ ] |
| 13.2.2 | Persists | Refresh the page | The card is still in its new column (the change was saved) | [ ] |
| 13.2.3 | Counts update | Watch the column counts after a move | Source count −1, destination count +1 | [ ] |
| 13.2.4 | Viewer cannot drag | Log in as **viewer**, open Mobile App Redesign, try dragging a card | Cards don't drag / no status change (read-only) | [ ] |
| 13.2.5 | Rollback on failure *(optional)* | DevTools → block `PATCH /tasks/*/status`, then drag | Card snaps back to the original column **and an error toast** appears ("Couldn't save your changes. Please try again." — H3); no silent loss | [ ] |

### 13.3 Filters & sort

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 13.3.1 | Open filter | Click **Filter** | A popover with Status, Priority, Due, Assignee, Labels, and "Show cancelled" sections | [ ] |
| 13.3.2 | Filter by status | Tick "In Progress" | Board shows only In Progress tasks; an active **filter chip** appears below the sub-nav | [ ] |
| 13.3.3 | Multiple filters | Add a Priority filter too | Filters combine; a chip per active filter | [ ] |
| 13.3.4 | Remove a chip | Click the × on a chip | That filter clears; results update | [ ] |
| 13.3.5 | Clear all | Click "Clear all" | All filters removed; full board returns | [ ] |
| 13.3.6 | Show cancelled | Enable "Show cancelled" in the filter | A **Cancelled** column appears with the cancelled tasks | [ ] |
| 13.3.7 | Sort | Pick "Priority" (then "Due date") from Sort | Card order within columns changes accordingly | [ ] |
| 13.3.8 | URL reflects state | Apply a filter + sort, look at the URL | The query string carries the filter/sort (shareable) | [ ] |
| 13.3.9 | Filtered-empty | Filter to a status with no matches | "No tasks match these filters." with a "Clear filters" link | [ ] |

### 13.4 Create Task modal (DRD §10.3) & Project Settings (DRD §10.2)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 13.4.1 | Open Create Task | As dev1, click **Create task** | Modal with Title (required), Description, Assignee, Priority, Due date, Labels | [ ] |
| 13.4.2 | Validation | Submit with empty title | Inline validation; submit blocked | [ ] |
| 13.4.3 | Create | Fill title + a couple of fields, submit | Toast "Task created."; modal closes; the new task appears in **Backlog** without a refresh | [ ] |
| 13.4.4 | Assignee options | Open the Assignee dropdown | Lists members with access to this project (+ yourself) — not the whole workspace | [ ] |
| 13.4.5 | Settings gear (Owner/Admin) | Log in as **Owner**, open the project, click the gear | Project Settings modal with **Details** and **Access** tabs | [ ] |
| 13.4.6 | Edit details | On Details, change the name, Save | Toast; name updates (reflected in sidebar/breadcrumb after refresh) | [ ] |
| 13.4.7 | Manage access | On Access, add/remove a member | Member list updates; "Add member" offers workspace Members/Viewers not already granted | [ ] |
| 13.4.8 | No gear for Member/Viewer | Log in as dev1 (Member) then viewer | The settings gear is **absent** | [ ] |

### 13.5 Empty board

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 13.5.1 | Empty project | Create a new project (§12.6) and open its board | "This project has no tasks yet." with a "Create a task" button (for non-Viewers) | [ ] |

---

## 14. List View (Phase G4) — DRD §8.5, PRD §9

From a project board, click **List** in the sub-nav toggle (URL `/projects/<id>/list`).

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 14.1 | Toggle to list | Click **List** | A table replaces the columns; same sub-nav, List now active | [ ] |
| 14.2 | Columns | Inspect the header row | Title, Status, Assignee, Priority, Due, Labels | [ ] |
| 14.3 | Row content | Inspect a row | Title; status badge; assignee (avatar + name); priority icon + label; due date (overdue flagged); label chips | [ ] |
| 14.4 | Sortable headers | Click **Priority**, then **Due**, then **Assignee** | Rows reorder by that column; the active sort column is indicated. (Title/Status are **not** sortable — expected) | [ ] |
| 14.5 | Inline status (editor) | As dev1, change a row's status via its dropdown | Status updates inline and persists on refresh | [ ] |
| 14.6 | Inline status (viewer) | Log in as **viewer** | The status cell is a read-only badge (no dropdown) | [ ] |
| 14.7 | Shared filter/sort | On the board, apply a filter; toggle to List | The same filter/sort is in effect on the list (state shared via URL) | [ ] |
| 14.8 | Row opens panel | Click a row's title | Opens the task detail panel (§15) | [ ] |
| 14.9 | Filtered-empty | Filter to no matches | "No tasks match these filters." + clear link | [ ] |
| 14.10 | Last-used view remembered | Switch a project to List, navigate away, reopen that project | It reopens on **List** (per-project last-used view, localStorage) | [ ] |

---

## 15. Task Detail Panel (Phase G5) — DRD §9, PRD §10/§11

Open from a board card, a list row, a dashboard task, or directly at `/projects/<id>/tasks/<taskId>`. Use **dev1** on **Mobile App Redesign**.

### 15.1 Open / close / layout

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 15.1.1 | Opens as overlay | Click a task card | A panel slides in from the right over the board; the board stays visible behind a dimmed backdrop | [ ] |
| 15.1.2 | Header | Inspect the panel header | Task title, a status control, and a close (×) button | [ ] |
| 15.1.3 | Close — × | Click × | Panel closes; you're back on the board/list | [ ] |
| 15.1.4 | Close — Esc | Reopen, press Esc | Panel closes | [ ] |
| 15.1.5 | Close — backdrop | Reopen, click the dimmed area outside the panel | Panel closes | [ ] |
| 15.1.6 | Deep link | Paste a `/projects/<id>/tasks/<taskId>` URL into a new tab (logged in) | The panel opens over that project's view | [ ] |
| 15.1.7 | Reduced motion | Enable OS "Reduce Motion", reopen | The slide-in is disabled/minimal | [ ] |

### 15.2 Properties (editors)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 15.2.1 | Properties shown | Inspect the panel | Status, Assignee, Priority, Due date, Labels rows | [ ] |
| 15.2.2 | Edit title | As dev1, click the title, change it, blur/Enter | Title saves; reflected on the card/list after refresh | [ ] |
| 15.2.3 | Change status | Use the status dropdown | Updates; the card moves columns on the board behind it without a refresh | [ ] |
| 15.2.4 | Change assignee | Pick a different member | Assignee updates | [ ] |
| 15.2.5 | Priority / due / labels | Change each | Each persists on refresh; due-date picker accepts a date; labels are multi-select | [ ] |
| 15.2.6 | Viewer read-only | Log in as **viewer**, open a task | All properties are read-only (no dropdowns/pickers); no comment box | [ ] |

### 15.3 Description (Markdown)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 15.3.1 | Rendered Markdown | Open a task with a description | Description renders formatted (bold, lists, links, code) — not raw `**` markup | [ ] |
| 15.3.2 | Edit | Click the description, type Markdown, blur | It saves and re-renders | [ ] |
| 15.3.3 | Links are safe | If a description has a link | It opens in a new tab; no raw HTML/script executes (sanitized) | [ ] |

### 15.4 Comments & @mentions (PRD §11, DRD §11.4)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 15.4.1 | Comments listed | Open a task that has seeded comments | Comments shown oldest-first: avatar, author, relative time, rendered body | [ ] |
| 15.4.2 | Post a comment | As dev1, type a comment, click **Comment** | It appears at the bottom; the input clears | [ ] |
| 15.4.3 | @mention autocomplete | Type `@` then a few letters of a member's name | A member dropdown appears, filtered; ↑/↓ + Enter (or click) inserts the handle (e.g. `@dana-engineer`) | [ ] |
| 15.4.4 | Mention notifies | Mention **viewer** in a comment, then log in as viewer | Viewer has a new notification + bell badge for the mention (§16) | [ ] |
| 15.4.5 | Mention rendering *(deferred)* | Look at a posted comment containing a mention | The mention shows as `@handle` text (teal-chip styling is deferred — note, don't fail) | [ ] |
| 15.4.6 | Viewer cannot comment | As viewer, open a task | No comment input box | [ ] |

---

## 16. Notifications (Phase G6) — DRD §8.6, PRD §15

Generate some first: as **dev1**, on Mobile App Redesign, (a) comment with `@vivian-watch` on a task, and (b) reassign a task to **dev2**. Then log in as the recipient.

> **Real-time (H1):** the bell badge now updates **live** — when a notification is generated for the logged-in user in another tab/session, the count should increment within ~1s without a refresh (see §19.3). A slow background poll is still a safety net.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 16.1 | Bell badge | Log in as **viewer** (mentioned above) | The header bell shows an unread count | [ ] |
| 16.2 | Open page | Click the bell | Navigates to `/notifications` | [ ] |
| 16.3 | List order | Inspect the list | Reverse chronological (newest first) | [ ] |
| 16.4 | Unread styling | Look at unread rows | Tinted background + a teal unread dot | [ ] |
| 16.5 | Sentence content | Read a notification | Describes the event (mention / assignment / status change / comment) with actor + task | [ ] |
| 16.6 | Click → read + navigate | Click an unread notification | It marks read (tint/dot clears) and navigates to the task (panel opens) | [ ] |
| 16.7 | Badge decrements | Return to a screen with the bell | Unread count dropped by the one you read | [ ] |
| 16.8 | Mark all as read | On the page, click "Mark all as read" | All rows become read; the bell badge clears | [ ] |
| 16.9 | Empty state | Log in as a user with no notifications (e.g. fresh signup) | "You're all caught up." | [ ] |
| 16.10 | Self-actions don't notify | As dev1, comment on your own task without mentioning anyone | No self-notification is created | [ ] |

---

## 17. Search (Phase G7) — DRD §11.1, PRD §12

Use the header search box. Log in as **Owner** (sees all projects).

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 17.1 | Focus / ⌘K | Click the search box, or press ⌘K (Ctrl+K) | The box focuses | [ ] |
| 17.2 | Results dropdown | Type a word you know is in task titles (e.g. part of a seeded title) | A dropdown of up to ~8 results: title (matched text highlighted), project name, status badge | [ ] |
| 17.3 | Debounce | Type quickly | Results settle after you pause (no request per keystroke) | [ ] |
| 17.4 | Keyboard nav | Press ↓ / ↑ | The active result moves; **Enter** opens that task (panel); **Esc** closes the dropdown | [ ] |
| 17.5 | Click result | Click a result | Navigates to that task (panel opens) | [ ] |
| 17.6 | No results | Search for `zzqqxx` | "No tasks match your search." | [ ] |
| 17.7 | Access scoping | Search the same term as **viewer** vs **Owner** | Viewer only sees results from projects they can access (no cross-project leakage) | [ ] |
| 17.8 | Cancelled excluded | Search a term that matches a cancelled task | Cancelled tasks don't appear (excluded by default) | [ ] |

---

## 18. Settings (Phase G8) — DRD §8.7–§8.10, PRD §4/§7/§20

### 18.1 Layout & access control

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 18.1.1 | Settings entry | Click **Settings** in the sidebar | Lands on `/settings/workspace` (redirect from `/settings`) | [ ] |
| 18.1.2 | Tabs | Inspect the sub-nav | Workspace, Members, Labels, Profile tabs (for Owner/Admin) | [ ] |
| 18.1.3 | Manage-only redirect | Log in as **dev1** (Member), visit `/settings/members` directly | Redirected to `/dashboard` (manage tabs are Owner/Admin only) | [ ] |
| 18.1.4 | Member tab visibility | As dev1, open Settings | Only **Profile** is reachable; Workspace/Members/Labels tabs are hidden | [ ] |
| 18.1.5 | Viewer | Repeat 18.1.3–4 as **viewer** | Same: only Profile | [ ] |

### 18.2 Workspace tab (DRD §8.7)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 18.2.1 | Prefilled name | As Owner, open Workspace | The workspace name ("Aurora Studio") is prefilled | [ ] |
| 18.2.2 | Rename | Change the name, Save | Toast; refresh persists the new name | [ ] |
| 18.2.3 | Validation | Clear the name, Save | Inline validation; submit blocked | [ ] |

### 18.3 Members tab (DRD §8.8, §10.4, §10.5)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 18.3.1 | Member table | As Owner, open Members | Rows for all 5 seed users: avatar, name, email, role, (remove) | [ ] |
| 18.3.2 | Invitation table | Below members | Any pending invitations with email, role, status badge (pending/accepted/expired), sent time, Resend | [ ] |
| 18.3.3 | Change role | Change dev2 from Member to Admin via the role dropdown | Role updates (refresh persists) | [ ] |
| 18.3.4 | Owner row protected | Look at the Owner's own row | No role dropdown / no Remove on the Owner | [ ] |
| 18.3.5 | Invite member | Click "Invite member" | Modal: email + role (Admin/Member/Viewer — **no Owner**) | [ ] |
| 18.3.6 | Send invite | Invite `newhire@example.com` as Member | Toast "Invitation sent."; appears in the invitations table; email lands in MailHog | [ ] |
| 18.3.7 | Duplicate guard | Invite an email already in the workspace | Graceful error ("already in this workspace"), no crash | [ ] |
| 18.3.8 | Resend | Click Resend on a pending invite | New email in MailHog | [ ] |
| 18.3.9 | Remove member | Click Remove on a non-owner member | Confirmation modal explaining consequences; confirm → member disappears; their tasks become unassigned | [ ] |
| 18.3.10 | Remove cancel | Open the remove modal, Cancel | No change | [ ] |

> Use a **throwaway** invite/member for destructive tests, or re-seed afterward.

### 18.4 Labels tab (DRD §8.9, §10.6/§10.7)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 18.4.1 | Label list | As Owner, open Labels | Seeded labels listed as colored chips with edit/delete | [ ] |
| 18.4.2 | Create label | Click "Create label" | Modal: name + an 8-swatch color palette + a live preview chip | [ ] |
| 18.4.3 | Create happy path | Name it, pick a color, submit | Toast; the label appears in the list (and is available on tasks) | [ ] |
| 18.4.4 | Edit label | Edit an existing label's name/color | Updates reflected in the list and on tasks using it | [ ] |
| 18.4.5 | Delete label | Delete a label | Confirmation modal ("removed from all tasks"); confirm → gone from the list and from any task that had it | [ ] |
| 18.4.6 | Empty state | Delete all labels (or a fresh workspace) | "No labels yet. Create your first label." | [ ] |

### 18.5 Profile tab (DRD §8.10, §10.8)

Available to **all** roles (own profile).

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 18.5.1 | Profile shown | Open Profile | Avatar, email (read-only), display name (editable) | [ ] |
| 18.5.2 | Save display name | Change the name, Save | Toast; the header user block updates (it reads `/auth/me`) | [ ] |
| 18.5.3 | Change password | Enter current + a new (≥8) password, Update | Success toast | [ ] |
| 18.5.4 | New password works | Log out, log in with the new password | Succeeds; old password rejected | [ ] |
| 18.5.5 | Wrong current password | Try changing with a wrong current password | Clear error ("incorrect"), no change | [ ] |
| 18.5.6 | Delete account (throwaway only) | On a **throwaway** account, open Delete Account, enter the password, confirm | Account deleted; you're logged out and sent to `/login`; the user can't log back in | [ ] |

> **Do NOT** delete a seed account you still need. Use the §7.2 fresh-signup account or re-seed afterward.

---

## 19. Real-time updates (Phase H1) — PRD §15.4/§19, TDD §10

The WebSocket bridge pushes server changes into the UI live. Best tested with **two browser contexts side by side** — either two tabs as the **same** user, or two separate browsers/profiles logged in as **different** users who share a project (e.g. **dev1** and **dev2**, both with access to **Mobile App Redesign**). Keep both windows visible at once; the receiving window should update **without a manual refresh**, typically within ~1 second.

> Connection mechanics: the socket connects after login and carries the CSRF token. On a dropped connection the app shows a discreet **"Reconnecting…"** pill (bottom-left) and, on reconnect, **resyncs** all data. Auth failures (`4401`/`4403`) end the session and route to `/login`.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 19.1 | Board move propagates | Window A & B both on Mobile App Redesign board (A=dev1, B=dev2). In A, drag a card to a new column | B's board reflects the move within ~1s — **no refresh** | [ ] |
| 19.2 | Task panel updates | B has the task panel open for task X; in A change task X's priority/assignee | B's open panel reflects the change live | [ ] |
| 19.3 | Notification badge live | In A (dev1) @mention **dev2** in a comment (or reassign a task to dev2) | B's (dev2) header bell badge increments live; opening §16 shows the new notification | [ ] |
| 19.4 | Comment appears live | B has task X's panel open; in A post a comment on task X | The comment appears in B's thread without a refresh | [ ] |
| 19.5 | Activity feed live | B on the dashboard; in A perform an action in a project B can see | B's Recent Activity gains the new entry live | [ ] |
| 19.6 | Reconnecting indicator | In one window, DevTools → Network → **Offline**, wait a few seconds | A "Reconnecting…" pill appears; restoring the network clears it and data resyncs | [ ] |
| 19.7 | @mention announced (a11y) | With a screen reader on, receive an @mention in another window | The mention is announced via the polite live region (TDD §10.3) | [ ] |
| 19.8 | No cross-workspace leakage | Window B logged into a **fresh-signup** workspace (§7.2); in A act within Aurora Studio | B receives **nothing** — events never cross workspaces | [ ] |

> If a receiving window only updates after a manual refresh, that's a **defect** now (it was expected behavior pre-H1). Brief lag (~1s) or a momentary "Reconnecting…" is normal.

---

## 20. Toasts & error feedback (Phase H3) — DRD §7.8/§18.2

Async actions give non-blocking **toast** feedback (bottom-right, dark pill, auto-dismiss ~5s, manually dismissable via the ×). Success toasts are exercised throughout (§12.6, §13.4, §16, §18); this section spot-checks the **error** path and toast mechanics.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 20.1 | Success toast | Create a project (§12.6.4) or save a setting | A success toast appears bottom-right and auto-dismisses after ~5s | [ ] |
| 20.2 | Manual dismiss | Trigger any toast, click its **×** before it auto-dismisses | The toast closes immediately | [ ] |
| 20.3 | Standardized error toast | DevTools → block a mutation (e.g. `PATCH /workspaces/me/members/*` then change a role; or block `DELETE /labels/*` then delete a label) | An error toast "Couldn't save your changes. Please try again." appears; the optimistic/UI change does not silently persist | [ ] |
| 20.4 | Inline errors still contextual | Enter a **wrong current password** in Profile → Change password (§18.5.5) | The error shows **inline** by the field (not just a toast) — contextual errors aren't replaced by the generic toast | [ ] |
| 20.5 | Reduced motion | Enable OS "Reduce Motion", trigger a toast | The toast appears without the fade-up animation | [ ] |

---

## 21. Accessibility & polish quick-checks

Lightweight manual pass. The automated `vitest-axe` pass (H4) is done; the full manual screen-reader/contrast sweep is tracked in `apps/web/docs/a11y-manual-checklist.md`.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 21.1 | Keyboard-only login | Tab through `/login`, submit with Enter | All fields reachable in logical order; visible focus rings; form submits via keyboard | [ ] |
| 21.2 | Field labels | Inspect inputs (login, Create Project/Task, Invite, Label, Profile) | Each field has an associated label (not placeholder-only) | [ ] |
| 21.3 | Error association | Trigger an inline error | Error text sits below the field and is announced/associated (DRD §18.1) | [ ] |
| 21.4 | Modal focus | Open any modal (Create Task, Invite, Confirm) | Focus moves into the modal; Esc closes it; focus returns to the trigger | [ ] |
| 21.5 | Confirm-dialog description | Open a destructive confirm (Remove member / Delete label) with a screen reader | The consequence sentence is announced (the dialog is described via `aria-describedby` — H4) | [ ] |
| 21.6 | Panel keyboard | Open the task panel | Esc closes it; controls are reachable by keyboard | [ ] |
| 21.7 | Search keyboard | Open search, arrow through results, Enter | Fully operable from the keyboard | [ ] |
| 21.8 | Reduced motion | Enable OS "Reduce Motion", reload | Transitions/animations (modals, panel slide-in, toasts) are disabled or minimal | [ ] |
| 21.9 | No console errors | Watch DevTools Console across all flows | No uncaught errors or React warnings during normal use | [ ] |
| 21.10 | Tokens applied | Visual scan across screens | Warm-neutral palette, Inter font, consistent spacing per the design system | [ ] |

---

## 22. Defect log

Record anything that deviates from **Expected**. Keep "expected-deferred" observations (see §1 out-of-scope) separate from real defects.

| ID | Test # | Severity | Summary | Steps to reproduce | Expected vs actual | Status |
|----|--------|----------|---------|--------------------|--------------------|--------|
| D1 | | | | | | |
| D2 | | | | | | |
| D3 | | | | | | |

**Severity guide:** Blocker (can't proceed) · Major (feature broken) · Minor (cosmetic/edge) · Observation (expected at this phase).

---

## 23. Sign-off

- [ ] All §5 (shell) checks pass
- [ ] All §6 (login) checks pass
- [ ] All §7 (signup) checks pass
- [ ] All §8–§9 (password reset) checks pass
- [ ] All §10 (accept invitation) checks pass (deferred items noted, not failed)
- [ ] All §11 (session) checks pass
- [ ] All §12 (dashboard) checks pass
- [ ] All §13 (board) checks pass
- [ ] All §14 (list) checks pass
- [ ] All §15 (task detail panel) checks pass
- [ ] All §16 (notifications) checks pass
- [ ] All §17 (search) checks pass
- [ ] All §18 (settings) checks pass
- [ ] All §19 (real-time) checks pass
- [ ] All §20 (toasts & errors) checks pass
- [ ] §21 accessibility quick-checks pass
- [ ] Defects logged in §22

**Tested by:** ________________  **Date:** ____________  **Build / commit:** ____________

> After sign-off, reset the database (`docker compose down -v && make dev && make seed`) so the next tester starts from clean, documented seed credentials.
