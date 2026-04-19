# Decision 001: Application Delivery Model

**Status:** Decided

**Category:** Platform & Topology

**Question:** How is TaskFlow delivered to end users — web application, native desktop, native mobile, or a combination?

**Decision:** Web application only, accessed via modern evergreen browsers. No native desktop or mobile applications are produced.

**Rationale:** Inherited from BRD PA-01 / PA-03 and Business Decision 020. A single web codebase minimizes maintenance for a demonstration project and keeps the stack surface small. A Progressive Web App may be considered later if installability is needed, but is not in scope.
