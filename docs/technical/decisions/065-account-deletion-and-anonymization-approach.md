# Decision 065: Account Deletion & Anonymization Approach

**Status:** Decided

**Category:** Data Layer

**Question:** How is "delete personal data, retain anonymized content" implemented?

**Options considered:**
- Null out FKs + delete user row
- In-place replacement (keep row, null out personal fields)
- Soft-delete pattern

**Decision:** In-place user replacement.

On account deletion:
1. `users.email` and `users.name` set to `NULL`.
2. `users.password_hash` set to `NULL`.
3. `users.deleted_at` set to `now()`.
4. Active sessions for this user deleted.
5. `tasks.assignee_id = NULL` for any tasks currently assigned.

Foreign keys from `tasks.created_by`, `comments.author_id`, `activity_events.actor_id`, `audit_log.actor_id`, and `notifications.actor_id` remain intact. The UI resolves a user row with `deleted_at IS NOT NULL` to a localized "Deleted user" display string and a neutral placeholder avatar.

Authentication checks (login, session validation, invitation accept) must refuse any user row where `deleted_at IS NOT NULL`. This is enforced in the auth layer, not left to callers.

**Rationale:** Keeping the row avoids null-FK fanout in history-bearing tables and preserves the integrity of activity feeds and audit logs. A single canonical "Deleted user" identity is the cleanest UX for anonymized historical records. Assignments are cleared because "assigned to a deleted user" is meaningless — the task becomes unassigned (PRD §20.2).
