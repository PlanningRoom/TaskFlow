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
| `auth.login.success` | User successfully logs in |
| `auth.login.failure` | Login attempt fails (bad password, unknown email, etc.) |
| `auth.logout` | User logs out or session expires |
| `auth.password_reset.requested` | Password reset token requested |
| `auth.password_reset.completed` | Password reset token consumed |
| `auth.password_changed` | Password changed while logged in |
| `workspace.user.role_changed` | Admin/Owner changes another user's role |
| `workspace.user.removed` | Owner removes a user |
| `workspace.invitation.sent` | Invitation sent |
| `workspace.invitation.accepted` | Invitation accepted |
| `account.deleted` | User deletes own account |

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
