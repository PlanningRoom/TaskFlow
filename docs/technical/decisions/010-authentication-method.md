# Decision 010: Authentication Method

**Status:** Decided

**Category:** Auth & Identity

**Question:** How do users prove identity to the application?

**Decision:** Email and password only. No social login, no magic links, no SSO, no MFA at launch.

**Rationale:** Inherited from PRD §3.1 and Product Decision 001. The simplest method that works without third-party dependencies. The implementation approach (library, hashing, sessions) is left to Decisions 047–050.
