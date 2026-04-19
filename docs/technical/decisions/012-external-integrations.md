# Decision 012: External Integrations

**Status:** Decided

**Category:** External Surface

**Question:** Which external services or tools does TaskFlow integrate with at launch?

**Decision:** None. No Slack, GitHub, calendar, email-in, or webhook integrations ship at launch.

**Rationale:** Inherited from BRD IA-01 and Business Decision 022. Keeps scope small and eliminates a class of auth, configuration, and error-handling work. Transactional email for invitations and password reset (Decision 067) is not considered an "integration" in this sense — it is an internal delivery channel.
