# Decision 072: Environments Topology

**Status:** Decided

**Category:** Ops & Observability

**Question:** What environments exist?

**Options considered:**
- Local dev + prod
- Local dev + preview-per-PR + prod
- Local dev + staging + prod
- Full — local dev + preview-per-PR + staging + prod

**Decision:** Two environments only:

- **Local dev** — Docker Compose on the developer's machine (Decision 039).
- **Production** — AWS EC2 t4g.small (Decision 036).

No staging. No preview environments per PR. E2E tests run in CI against an ephemeral `docker compose up` stack.

**Rationale:** Single-contributor demo project. Staging would double the AWS bill for a "just in case" environment that sees no traffic. Preview-per-PR is valuable for visual review but expensive to provision on AWS — CI's headless Playwright run is a sufficient substitute for a demo. If the project grows, a staging environment is a CloudFormation template away.
