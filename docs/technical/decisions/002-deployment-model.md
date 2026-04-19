# Decision 002: Deployment Model

**Status:** Decided

**Category:** Platform & Topology

**Question:** Is TaskFlow a cloud-hosted SaaS, a self-hosted package, or both?

**Decision:** Cloud-hosted SaaS only. No self-hosted distribution at launch.

**Rationale:** Inherited from BRD DI-01 and Business Decision 018. A hosted model gives full control over infrastructure, simplifies real-time delivery (Decision 007), and removes the need to support arbitrary customer environments. Self-hosting can be revisited later; the single-tenant architecture (Decision 003) leaves that door open.
