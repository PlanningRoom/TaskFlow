# Decision 040: API Style

**Status:** Decided

**Category:** API & Real-Time

**Question:** What RPC/HTTP style does the internal API use?

**Options considered:**
- REST (JSON over HTTP)
- GraphQL
- tRPC (not applicable — cross-language)
- RPC-over-HTTP

**Decision:** REST. JSON request and response bodies. Resource-oriented URLs (`/api/v1/projects/:id/tasks`). FastAPI generates an OpenAPI 3.1 schema automatically.

**Rationale:** REST is the safe choice for a future-public API (Decision 013), widely understood, and maps cleanly to FastAPI's routing model. tRPC is ruled out by the cross-language stack (Decisions 027/028). GraphQL adds a schema layer and query complexity that is overkill for a demonstration project.
