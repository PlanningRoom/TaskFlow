# Decision 084: Audit Logging Scope

**Status:** Decided

**Category:** Security Hardening

**Question:** Which administrative actions are audit-logged?

**Options considered:**
- No audit log
- Dedicated `audit_log` table for security-sensitive events
- Full mutation audit (before/after)

**Decision:** Dedicated `audit_log` table for security-sensitive events.

Events logged:

| Event Type | Trigger |
|---|---|
| `auth.signup` | New workspace + Owner created via sign-up |
| `auth.login.success` | User successfully logs in |
| `auth.login.failure` | Login attempt fails (bad password, unknown email, etc.) |
| `auth.logout` | User logs out or session expires |
| `auth.password_reset.requested` | Password reset token requested |
| `auth.password_reset.completed` | Password reset token consumed |
| `auth.password_changed` | Password changed while logged in |
| `auth.profile.updated` | Authenticated profile mutation (display name) |
| `workspace.user.role_changed` | Admin/Owner changes another user's role |
| `workspace.user.removed` | Owner removes a user |
| `workspace.invitation.sent` | Invitation sent |
| `workspace.invitation.resent` | Invitation token regenerated and re-emailed |
| `workspace.invitation.accepted` | Invitation accepted |
| `account.deleted` | User deletes own account |
| `workspace.updated` | Owner/Admin renames the workspace |
| `workspace.label.created` | Owner/Admin creates a label |
| `workspace.label.updated` | Owner/Admin edits a label |
| `workspace.label.deleted` | Owner/Admin deletes a label |
| `project.created` | A user creates a project |
| `project.updated` | Owner/Admin edits project name/description/color |
| `project.access.added` | Owner/Admin grants a user project access |
| `project.access.removed` | Owner/Admin revokes a user's project access |

Naming convention: `{domain}.{subaction}` where subaction may be a single token (`account.deleted`, `auth.password_changed`) or `{noun}.{verb}` for compound subjects (`auth.password_reset.requested`, `workspace.user.role_changed`). The `event_type` column has a CHECK constraint pinning the table above; adding a new event requires a migration that extends the constraint.

Schema:

| Column | Type |
|---|---|
| `id` | `uuid` PK |
| `actor_id` | `uuid` FK → users, nullable (login failure may not know user) |
| `event_type` | `text` |
| `target_id` | `uuid`, nullable |
| `ip` | `inet` |
| `user_agent` | `text` |
| `metadata` | `jsonb` |
| `created_at` | `timestamptz`, indexed |

Append-only. No UI at launch; queried via Logs Insights + direct DB access. Retained indefinitely (unlike CloudWatch logs at 30 days).

**Rationale:** BRD §7.5 excludes formal compliance, but a minimal audit trail costs little and gives us debug visibility for auth incidents (a brute-force attempt, an unexpected role change). Distinct from the activity feed, which captures user-facing content changes.

**Scope boundary with `activity_events` (Decision 063):** task / comment lifecycle events live in `activity_events`, NOT here. The `audit_log` is for security-sensitive admin actions (auth, role changes, member removal, label/project administration, project-access grants/revocations). Routine content mutations stay in the activity feed. Migrating an event between tables would be a breaking change to log-mining queries.
