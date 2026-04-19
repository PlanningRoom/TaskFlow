# Decision 049: Password Reset Flow

**Status:** Decided

**Category:** Auth Implementation

**Question:** How do users reset a forgotten password?

**Options considered:**
- Emailed reset token with a dedicated form
- Magic-link that auto-logs-in to a forced-reset page
- Admin-only reset

**Decision:** Emailed reset token.

Flow:
1. User submits email on the "Forgot password" page. Endpoint always responds 200 (no account enumeration).
2. If the account exists: generate a 32-byte random token, store its SHA-256 hash in `password_reset_tokens` with `user_id`, `expires_at = now + 1h`, `used_at = null`.
3. SES sends an email containing a link to `https://{host}/reset-password?token={raw_token}`.
4. On submit, server looks up the hashed token, verifies it is unexpired and unused, marks `used_at`, updates the user's password hash, and deletes all active sessions for that user.

Tokens are single-use. Only the most recent token per user is valid — submitting a new request invalidates earlier tokens.

**Rationale:** Standard pattern, no account enumeration surface, short TTL limits the window for a stolen email. Deleting active sessions on reset is a key security step — a compromised session cannot survive a password reset.
