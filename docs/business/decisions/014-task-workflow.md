# Decision 014: Task Workflow

**Status:** Decided

**Category:** Workflow Model

**Question:** How should tasks flow through statuses — a simple model (e.g., to-do/in-progress/done) or complex multi-stage workflows?

**Decision:** Extended fixed statuses with Cancelled. The default workflow is: **Backlog → To Do → In Progress → In Review → Done**, with **Cancelled** as a terminal status for abandoned tasks.

**Rationale:** These statuses cover the most common workflow stages and are universally understood across industries. "In Review" is broadly applicable (code review, stakeholder approval, quality check). Cancelled handles abandoned tasks to keep the workspace clean. This provides enough structure for medium teams without being rigid.
