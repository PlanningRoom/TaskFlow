# Decision 019: Tenancy Model

**Status:** Decided

**Category:** Deployment Model

**Question:** Will TaskFlow use a multi-tenant or single-tenant architecture?

**Decision:** Single-tenant. TaskFlow will run as a single dedicated instance.

**Rationale:** As a demonstration project, there is no need to support multiple tenants. A single-tenant architecture simplifies the application code by eliminating tenant-scoping concerns and provides the strongest data isolation.
