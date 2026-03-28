# Decision 013: Label Scope

**Status:** Decided

**Category:** Labels & Tags

**Question:** Are labels shared across the entire workspace, or does each project have its own independent set of labels?

**Decision:** Labels are workspace-wide. A single set of labels is shared across all projects.

**Rationale:** Workspace-wide labels are simpler to manage — Admins maintain one label set instead of duplicating labels per project. Shared labels also enable consistent cross-project filtering and searching (e.g., find all tasks labeled "design" across every project). This aligns with TaskFlow's philosophy of consistency — just as task statuses are the same across every project, labels provide a shared vocabulary for categorization.
