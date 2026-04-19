# Decision 003: Tenancy Architecture

**Status:** Decided

**Category:** Platform & Topology

**Question:** Does TaskFlow run as a multi-tenant shared instance or as single-tenant instances?

**Decision:** Single-tenant architecture — one dedicated instance serves the TaskFlow application. Workspaces are logical tenants within that instance (each user belongs to exactly one workspace).

**Rationale:** Inherited from BRD DI-02 and Business Decision 019. For a demonstration project this is the simpler model operationally. Logical workspace isolation at the application layer is sufficient; physical tenant isolation is not required. Every query that touches workspace-scoped data must filter by workspace id.
