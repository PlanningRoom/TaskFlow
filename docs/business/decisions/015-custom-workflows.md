# Decision 015: Custom Workflows

**Status:** Decided

**Category:** Workflow Model

**Question:** Do teams need the ability to define custom workflows per project or team?

**Decision:** No. Fixed statuses only. All projects use the same workflow defined in Decision 014.

**Rationale:** The fixed statuses (Backlog, To Do, In Progress, In Review, Done, Cancelled) are general enough for most use cases. Custom workflows would add disproportionate complexity to the data model, UI, and cross-project features like dashboards and filters. This can be revisited as a future enhancement.
