# Decision 063: Activity Feed Storage Model

**Status:** Decided

**Category:** Data Layer

**Question:** How are activity feed entries produced and stored?

**Options considered:**
- Append-only events table in the same transaction as mutations
- Derived from source-table timestamps
- Event sourcing
- CDC via logical replication

**Decision:** Append-only `activity_events` table. Rows written in the same DB transaction as the triggering mutation via a thin service-layer helper.

Schema:

| Column | Type |
|---|---|
| `id` | `uuid`, primary key |
| `workspace_id` | `uuid`, FK, indexed |
| `project_id` | `uuid`, FK, nullable, indexed |
| `actor_id` | `uuid`, FK → users |
| `event_type` | `text` — enum: `task.created`, `task.status_changed`, `task.assigned`, `task.unassigned`, `comment.created` |
| `subject_type` | `text` — `task`, `comment`, `project` |
| `subject_id` | `uuid` |
| `metadata` | `jsonb` — type-specific payload (e.g. `{"from": "todo", "to": "in_progress"}`) |
| `created_at` | `timestamptz`, indexed |

Indexes: `(workspace_id, created_at DESC)`, `(project_id, created_at DESC)`, `(actor_id, created_at DESC)`.

**Rationale:** Append-only is simple, cheap, and gives both dashboard-wide (PRD §13.2) and project-scoped (PRD §14.2) feeds from the same table. Writing in the same transaction as the mutation guarantees consistency — no "activity missing because the worker was down" class of bug. Same rows drive the Postgres NOTIFY that fans out to WebSockets (Decision 045).
