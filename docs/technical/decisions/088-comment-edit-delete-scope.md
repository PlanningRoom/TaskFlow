# Decision 088: Comment Edit / Delete Scope

**Status:** Decided

**Category:** Product / Permissions

**Question:** Who can edit or delete a comment after it has been posted?

**Options considered:**
- Author only — only the user who wrote the comment can modify or delete it.
- Author + Owner/Admin moderation — author can edit/delete; Owner/Admin can delete (but not edit) any comment.
- Append-only — no edit or delete in v1.

**Decision:** **Author only.**

`PATCH /api/v1/comments/:id` and `DELETE /api/v1/comments/:id` are permitted only when the calling user is `comment.author_id`. Any other user — including Owner and Admin — receives `403 PERMISSION_DENIED`. Roles with the `ADD_COMMENT` action can post; nobody else can mutate someone else's comment.

The comment row's `updated_at` advances on edit; the `body` is replaced; mentions are re-parsed from the new body. Deletion is a hard delete (no soft-delete column).

**Rationale:** Resolves Open Item #1 from `docs/planning/implementation-plan.md` §6.4. PRD §11.3 explicitly defers this question to implementation; we want a rule that's predictable and avoids the moderation question for v1. If moderation needs surface, a follow-up ADR can extend the rule (e.g., "Owner/Admin may delete with an audit log entry").

This decision does NOT add a new audit-log event type — comment edits/deletes go through the activity feed only via the originating `comment.created` event, and the comment table itself records the edit timestamp. Per ADR 084, audit events stay scoped to security-sensitive admin actions.
