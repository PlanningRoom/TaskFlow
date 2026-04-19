# Decision 070: Notification Dispatch Architecture

**Status:** Decided

**Category:** Supporting Services

**Question:** When a notification-triggering event occurs, how does it reach the right users in real time?

**Options considered:**
- Synchronous in the mutation transaction
- Asynchronous via a worker
- Hybrid

**Decision:** Synchronous.

Flow when a notification-triggering event occurs (comment with @mention, task assignment, status change on someone's task, comment on someone's task):

1. Mutation's DB transaction inserts the primary row (comment, task update) AND the corresponding `notifications` rows (Decision 064) AND the `activity_events` row (Decision 063).
2. On transaction commit, a Postgres `NOTIFY notifications, '{recipient_id}'` fires per recipient.
3. WebSocket handlers (Decision 045) subscribed to their user's channel receive the payload, fetch the new notification(s), and push the update to the connected browser — badge count increments, notifications page updates in real time.
4. If the recipient is not currently connected, the row is simply present on next page load.

**Rationale:** Synchronous dispatch minimizes latency (PRD §15.4 requires real-time notification delivery). The hot path cost is small — even an @-heavy comment is maybe 10 additional rows. Putting the notification write in the same transaction as the mutation eliminates "the comment saved but the notification didn't" bugs.
