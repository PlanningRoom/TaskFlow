# Decision 002: Invitation Flow

**Status:** Decided

**Category:** Authentication & Onboarding

**Question:** How do workspace invitations behave — do they expire? Can they be resent? What happens if an invited email already has an account?

**Decision:** Invitations expire after 7 days and can be resent by Owners and Admins. Admins have visibility into invitation status (pending, accepted, expired). Revocation is not supported at launch. If the invited email belongs to an existing TaskFlow user, accepting the invitation adds them to the workspace with the assigned role — no new account creation is needed.

**Rationale:** Expiring invitations keep the system tidy and reduce the security risk of old links lingering in inboxes. Resend gives admins a recovery path when invitations are missed or expire. Revocation adds complexity for a rare edge case and is not justified for a demonstration project. Adding existing users directly on acceptance is the simplest and most intuitive behavior — no extra steps or confusion for either the admin or the invitee.
