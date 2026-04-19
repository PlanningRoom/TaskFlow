# Decision 007: Real-Time Update Requirement

**Status:** Decided

**Category:** Platform & Topology

**Question:** Must TaskFlow deliver real-time updates across clients, or is polling acceptable?

**Decision:** Real-time updates are a core requirement. Board changes, task edits, comments, and notifications propagate to connected clients without manual refresh. Notification badge counts update in real time.

**Rationale:** Inherited from BRD CC-05, PRD §15.4 and §19, and Business Decision 017. This drives the need for a persistent client-server channel; transport and infrastructure choices are deferred to Decisions 044 and 045.
