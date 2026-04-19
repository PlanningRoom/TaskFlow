# Decision 064: Notification Storage Model

**Status:** Decided

**Category:** Data Layer

**Question:** How are in-app notifications stored and queried?

**Options considered:**
- Dedicated `notifications` table
- Derived view over `activity_events`
- Hybrid

**Decision:** Dedicated `notifications` table.

Schema:

| Column | Type |
|---|---|
| `id` | `uuid` PK |
| `recipient_id` | `uuid`, FK → users, indexed |
| `actor_id` | `uuid`, FK → users |
| `event_type` | `text` — `mention`, `task_assigned`, `task_status_changed`, `task_commented` |
| `task_id` | `uuid`, FK → tasks |
| `project_id` | `uuid`, FK → projects |
| `metadata` | `jsonb` |
| `read_at` | `timestamptz`, nullable |
| `created_at` | `timestamptz` |

Indexes: `(recipient_id, created_at DESC)` for the notifications page; partial `(recipient_id) WHERE read_at IS NULL` for the unread badge count (PRD §15.2).

Self-triggered actions do not produce notifications (PRD §15.1). This is enforced in the service layer — we don't write a notification row if `actor_id == recipient_id`.

**Rationale:** Dedicated table is the simplest way to support read/unread state, "mark all read" (PRD §15.2), and sub-ms unread count queries. A derived view would struggle with `read_at` state and require joins on every badge check.
