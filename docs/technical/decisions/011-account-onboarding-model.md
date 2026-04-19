# Decision 011: Account Onboarding Model

**Status:** Decided

**Category:** Auth & Identity

**Question:** How do new users gain access to a workspace?

**Decision:** Invite-only. Users join a workspace only when an Owner or Admin sends them an invitation. The sole public signup path creates a brand-new workspace (the signer becomes its Owner). Invitations expire after 7 days and can be resent.

**Rationale:** Inherited from BRD §3.1, PRD §3.3, and Business Decision 001. No public registration to join existing workspaces — this keeps the auth surface small and eliminates a whole class of abuse vectors (signup spam, enumeration). The invite flow has real architectural implications: a `invitations` table with expiry, a token URL pattern, and email delivery (Decision 067).
