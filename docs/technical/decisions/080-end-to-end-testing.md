# Decision 080: End-to-End Testing

**Status:** Decided

**Category:** Quality & Workflow

**Question:** Which tool runs browser-based E2E tests, and which journeys are covered?

**Options considered:**
- Playwright
- Cypress
- WebdriverIO
- None

**Decision:** Playwright. Tests run against a full `docker compose up` stack seeded from Decision 066.

Smoke journeys covered at launch:

1. **Signup → create workspace → create first project** (Owner).
2. **Accept invitation** (new user joins existing workspace).
3. **Create task → drag to In Progress → add comment with @mention → mark Done** (Member).
4. **Verify real-time update across two browser contexts** — one context moves a task, the other observes the board update without refresh.
5. **@mention delivers a notification in real time** — second context sees badge count increment.
6. **Search and filter** — create distinct tasks, search for one by keyword, filter by status/label/assignee, verify results.

Runs in CI on every PR (Decision 082) and locally via `make e2e`.

**Rationale:** The real-time multi-context test is especially valuable — the entire point of Decision 007 is cross-user real-time delivery, and only a full-browser test validates it end to end. Playwright's multi-context support is best-in-class for this.
