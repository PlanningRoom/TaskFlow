# Decision 018: Notification Trigger Events

**Status:** Decided

**Category:** Notifications

**Question:** Which specific events generate in-app notifications — @mentions only, or also task assignments, status changes on your tasks, comments on tasks you're assigned to, and/or other events?

**Decision:** The following events generate in-app notifications:

- **@mentioned in a comment** — you are directly mentioned by another user
- **Task assigned to you** — a task is newly assigned to you or reassigned to you
- **Status change on your task** — a task you are assigned to is moved to a different status by someone else
- **Comment on your task** — someone comments on a task you are assigned to

Notifications are not generated for your own actions (e.g., you won't be notified when you move your own task).

**Rationale:** These four triggers cover the core collaboration needs from the BRD (CC-03, CC-04): knowing when someone needs your attention, when you have new work, when your work's status changes, and when there's discussion on your tasks. Excluding self-triggered notifications prevents noise. This set is focused enough to be useful without overwhelming users, and aligns with the fixed notification model (Decision 019).
