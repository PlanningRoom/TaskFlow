# Decision 001: Authentication Method

**Status:** Decided

**Category:** Authentication & Onboarding

**Question:** How do users authenticate with TaskFlow — email/password, social login (Google, GitHub), magic links, or some combination?

**Decision:** Email/password only. Users sign up and log in using an email address and password. No social login or magic link options are provided at launch.

**Rationale:** TaskFlow is a demonstration project with no budget for third-party services. Email/password is the simplest authentication method to implement, has no external dependencies, and is universally understood. Since TaskFlow is invite-only, signup friction is a one-time event per user rather than a conversion concern. The auth system can be extended to support additional methods (social login, magic links) in the future without rearchitecting.
