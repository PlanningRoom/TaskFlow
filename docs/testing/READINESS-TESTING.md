# TaskFlow — Readiness Test Plan (through Phase G1)

**Version:** 1.0
**Date:** 2026-05-31
**Scope:** Manual UI testing of everything built **through Phase G1 — Auth Screens**.
**Audience:** Whoever is clicking through the running app to confirm it behaves.

---

## 1. What this covers

Phase G1 delivers the **unauthenticated journey**: Login, Sign Up, Accept Invitation, and Password Reset (request + confirm). These screens render *outside* the app shell. Once you authenticate, you land in the **app shell** (built in Phase F4) — sidebar, header, and a route tree of mostly **placeholder** screens.

So this plan tests three things, in order of how built-out they are:

1. **Auth screens (G1)** — fully functional, test thoroughly.
2. **App shell + routing (F4)** — functional chrome; navigation, breadcrumb, responsive behavior.
3. **Everything past the shell (G2–G8)** — *placeholders only*. Confirm they load without crashing; do **not** test for real content.

### Out of scope (not built yet — don't file these as bugs)

- Dashboard content, board, list, task detail, notifications page, search results, settings tabs — all are **placeholder components** until Phases G2–G8.
- Real-time updates (WebSocket bridge is Phase H1).
- Toasts as a global system (Phase H3) — G1 may show inline feedback instead.
- Tablet icon-rail and mobile hamburger overlay polish — **deferred** per the F4 status note. Below `md`, the sidebar is simply hidden.

> If a screen past the shell looks empty or unstyled, that's expected at this phase. Note it under "Observations," not "Defects."

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
| `owner@aurora.test` | Aurora Owens | Owner |
| `admin@aurora.test` | Adam Min | Admin |
| `dev1@aurora.test` | Dana Engineer | Member |
| `dev2@aurora.test` | Mason Code | Member |
| `viewer@aurora.test` | Vivian Watch | Viewer |

> Note: each user belongs to exactly one workspace. Signing up creates a *brand-new* workspace with you as Owner — it does **not** join Aurora Studio. To join Aurora Studio you'd need an invitation.

---

## 4. How to use this plan

- Work top-to-bottom; later sections assume earlier ones passed.
- Each test has a **Steps** list and an **Expected** result. Tick the checkbox if it matches.
- Use a **fresh browser profile or incognito window** per auth journey so stale cookies don't mask bugs. Keep **DevTools → Application → Cookies** and the **Console** tab open throughout.
- Log anything that fails in §13 (Defect Log).

**Reference specs** if you need to settle "is this a bug?": DRD §8.1 (Login/Signup), §8.2 (Accept Invitation), §18.1 (Inline validation) · PRD §3 (Auth) · TDD §11 (Sessions/cookies).

---

## 5. App shell & routing (Phase F4)

Test these while logged in as **Owner** (log in first via §6 if needed).

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 5.1 | Shell renders | Log in, observe layout | Sidebar (240px, left) + header (52px, top) + content area | [ ] |
| 5.2 | Sidebar nav | Inspect sidebar | Logo block; Dashboard + Notifications links; Projects section; bottom Settings link + user identity block | [ ] |
| 5.3 | Header | Inspect header | Breadcrumb, search input (⌘K hint), notification bell, user avatar | [ ] |
| 5.4 | Active nav state | Click Dashboard, then Notifications | The current route's nav item is visually highlighted | [ ] |
| 5.5 | Breadcrumb updates | Navigate between routes | Breadcrumb reflects current route | [ ] |
| 5.6 | Bare project URL redirect | Visit `/projects/<any-id>` directly | Redirects to `…/board` | [ ] |
| 5.7 | Placeholder routes load | Visit `/dashboard`, `/notifications`, `/settings/profile` | Each loads inside the shell without crashing (content may be a placeholder — expected) | [ ] |
| 5.8 | Responsive (desktop) | Window ≥ `md` width | Sidebar visible alongside content | [ ] |
| 5.9 | Responsive (narrow) | Shrink below `md` | Sidebar hides cleanly; content reflows (icon-rail/hamburger polish is deferred — not a bug) | [ ] |
| 5.10 | Unauth routes are shell-free | Log out, visit `/login`, `/signup` | Rendered as centered cards, NOT inside the sidebar/header shell | [ ] |

---

## 6. Login (DRD §8.1, PRD §3.2)

Use an incognito window. Start at http://localhost:5173 — unauthenticated, you should be routed to `/login`.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 6.1 | Layout | Observe `/login` | Centered card (~400px), logo above form, "Welcome back" heading, email + password fields, full-width primary button, footer link to sign up | [ ] |
| 6.2 | Happy path | Enter `owner@aurora.test` / `correct-horse-battery-staple`, submit | Logs in, redirects to `/dashboard` (placeholder content is fine) | [ ] |
| 6.3 | Session cookie set | After 6.2, DevTools → Application → Cookies | Session cookie present with `HttpOnly`, `Secure`*, `SameSite=Lax` (*Secure may be relaxed on `http://localhost` — note if so) | [ ] |
| 6.4 | Wrong password | Correct email, wrong password | Inline/error message; **no** redirect; message does NOT reveal whether the email exists | [ ] |
| 6.5 | Unknown email | `nobody@aurora.test` / anything | Same generic failure as 6.4 (no account enumeration) | [ ] |
| 6.6 | Empty fields | Submit blank form | Inline validation on required fields (on blur and on submit per DRD §18.1) | [ ] |
| 6.7 | Malformed email | `notanemail`, any password | Inline email-format validation before/at submit | [ ] |
| 6.8 | Link to signup | Click footer link | Navigates to `/signup` | [ ] |
| 6.9 | Already logged in | While authenticated, visit `/login` | Reasonable behavior (redirect to dashboard or render) — note actual behavior | [ ] |
| 6.10 | Each role logs in | Repeat 6.2 for admin / dev1 / viewer | All four succeed and land in the shell | [ ] |

---

## 7. Sign Up (DRD §8.1, PRD §3.1)

Sign-up creates a **new workspace** with you as Owner. Use a fresh incognito window.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 7.1 | Layout | Observe `/signup` | Same card shell as login; heading "Create your workspace"; footer link to login | [ ] |
| 7.2 | Happy path | Enter a new email (e.g. `tester+1@example.com`), valid password (≥ 8 chars), submit | Account created, logged in as Owner of a brand-new empty workspace, redirected into the shell | [ ] |
| 7.3 | New workspace is empty | After 7.2, look at dashboard/projects | No Aurora Studio data — confirms isolation (workspace-per-signup) | [ ] |
| 7.4 | Password too short | Password of < 8 chars | Inline validation; submit blocked (backend enforces min 8) | [ ] |
| 7.5 | Malformed email | `bad-email` | Inline email-format validation | [ ] |
| 7.6 | Duplicate email | Sign up again with an email already used | Graceful error, no crash, no silent overwrite | [ ] |
| 7.7 | Required fields | Submit blank | Inline validation on each required field | [ ] |
| 7.8 | Switch to login | Click footer link | Navigates to `/login` | [ ] |

---

## 8. Password Reset — Request (PRD §3, TDD §11)

This flow emails a reset link, caught by **MailHog** (http://localhost:8025).

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 8.1 | Reach the screen | From `/login`, click the password-reset link | Reset-request screen with an email field | [ ] |
| 8.2 | Request for real user | Enter `dev2@aurora.test`, submit | Generic "if an account exists, we've sent a link" style confirmation (no-enumeration) | [ ] |
| 8.3 | Email arrives | Open MailHog | A password-reset email is present for `dev2@aurora.test` with a reset link | [ ] |
| 8.4 | Request for unknown email | Enter `ghost@aurora.test`, submit | **Same** generic confirmation as 8.2; **no** email in MailHog (no enumeration) | [ ] |
| 8.5 | Malformed email | `nope` | Inline validation before submit | [ ] |

---

## 9. Password Reset — Confirm (PRD §3, TDD §11)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 9.1 | Open valid link | Click the reset link from the 8.3 email | Reset-confirm screen with new-password field(s) | [ ] |
| 9.2 | Set new password | Enter a valid new password, submit | Success; routed to login (or auto-logged-in — note actual) | [ ] |
| 9.3 | Log in with new password | Go to `/login`, use `dev2@aurora.test` + the new password | Login succeeds | [ ] |
| 9.4 | Old password rejected | Try logging in with `correct-horse-battery-staple` for dev2 | Fails (password was changed) | [ ] |
| 9.5 | Token is single-use | Re-open the same reset link from 9.1 | Rejected / expired state — link cannot be reused | [ ] |
| 9.6 | Sessions revoked | If dev2 was logged in elsewhere before reset | That session is invalidated (TDD §11 — reset revokes sessions) | [ ] |
| 9.7 | Short new password | Enter < 8 chars on confirm | Inline validation; submit blocked | [ ] |

> **Reset dev2's password back** to `correct-horse-battery-staple` afterward, or re-run `make seed` against a fresh DB, so later runs use the documented credential.

---

## 10. Accept Invitation (DRD §8.2, PRD §3.3)

Invitations are normally sent from Settings → Members (Phase G8, **not built yet**). For G1 you're testing the **accept** screen. To generate a real invitation token without the UI, send one via the API as Owner, then read the link from MailHog.

**Generate an invitation (one-time setup for this section):**

```bash
# 1. Log in as Owner and capture cookies
curl -s -c /tmp/tf-cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"owner@aurora.test","password":"correct-horse-battery-staple"}'

# 2. Read the CSRF token cookie value from /tmp/tf-cookies.txt, then send an invitation.
#    (Invitation send is CSRF-protected; pass the csrf cookie value in the header.)
curl -s -b /tmp/tf-cookies.txt -X POST http://localhost:8000/api/v1/workspaces/me/invitations \
  -H 'Content-Type: application/json' \
  -H 'X-CSRF-Token: <paste csrf cookie value>' \
  -d '{"email":"newhire@example.com","role":"member"}'
```

Then open MailHog → the invitation email → copy the `/invitations/<token>` link into a fresh incognito window.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 10.1 | New-user accept screen | Open the invitation link (email not yet a user) | Shows workspace name, inviter, assigned role; account-creation form with email **pre-filled** + display name + password | [ ] |
| 10.2 | Complete new-user accept | Fill display name + password, submit | Account created, joined Aurora Studio with the invited role, logged in, lands in shell | [ ] |
| 10.3 | Existing-user accept | Invite an email that's already a user, open link | Confirmation message + "Join workspace" button (no account-creation form) | [ ] |
| 10.4 | Expired/invalid token | Open `/invitations/totally-bogus-token` | Error state directing the user to ask an admin to resend (no crash) | [ ] |
| 10.5 | Email pre-fill is locked | On the new-user form | Email field reflects the invited address and isn't freely editable to a different identity | [ ] |

> Existing-user accept (10.3) **replaces** their workspace membership per PRD §3.3 — only test this with a throwaway user you don't need elsewhere, or skip it.

---

## 11. Session & logout behavior (TDD §11)

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 11.1 | Logout | While logged in, trigger logout (user menu in header) | Session cookie cleared; redirected to `/login` | [ ] |
| 11.2 | Protected route while logged out | After logout, visit `/dashboard` directly | Redirected to `/login` (not shown the shell) | [ ] |
| 11.3 | Refresh persists session | Log in, hard-refresh the page | Stays logged in (session cookie survives reload) | [ ] |
| 11.4 | `/auth/me` drives identity | Log in, check the header user block | Shows the correct display name / initials / avatar color for the logged-in user | [ ] |

---

## 12. Accessibility & polish quick-checks

Lightweight manual pass — full a11y sweep is Phase H4.

| # | Test | Steps | Expected | ✓ |
|---|------|-------|----------|---|
| 12.1 | Keyboard-only login | Tab through `/login`, submit with Enter | All fields reachable in logical order; visible focus rings; form submits via keyboard | [ ] |
| 12.2 | Field labels | Inspect inputs | Each field has an associated label (not placeholder-only) | [ ] |
| 12.3 | Error association | Trigger an inline error | Error text sits below the field and is announced/associated (DRD §18.1) | [ ] |
| 12.4 | Reduced motion | Enable OS "Reduce Motion", reload | Transitions/animations are disabled or minimal | [ ] |
| 12.5 | No console errors | Watch DevTools Console across all flows | No uncaught errors or React warnings during normal use | [ ] |
| 12.6 | Tokens applied | Visual scan | Warm-neutral palette, Inter font, consistent spacing per the design system | [ ] |

---

## 13. Defect log

Record anything that deviates from **Expected**. Keep "expected-placeholder" observations separate from real defects.

| ID | Test # | Severity | Summary | Steps to reproduce | Expected vs actual | Status |
|----|--------|----------|---------|--------------------|--------------------|--------|
| D1 | | | | | | |
| D2 | | | | | | |
| D3 | | | | | | |

**Severity guide:** Blocker (can't proceed) · Major (feature broken) · Minor (cosmetic/edge) · Observation (expected at this phase).

---

## 14. Sign-off

- [ ] All §5 (shell) checks pass
- [ ] All §6 (login) checks pass
- [ ] All §7 (signup) checks pass
- [ ] All §8–§9 (password reset) checks pass
- [ ] All §10 (accept invitation) checks pass
- [ ] All §11 (session) checks pass
- [ ] §12 quick-checks pass
- [ ] Defects logged in §13

**Tested by:** ________________  **Date:** ____________  **Build / commit:** ____________

> After sign-off, reset the database (`docker compose down -v && make dev && make seed`) so the next tester starts from clean, documented seed credentials.
