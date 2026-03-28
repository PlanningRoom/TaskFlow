# Decision 007: Task Relationships

**Status:** Decided

**Category:** Task Features

**Question:** Can tasks have relationships to other tasks — subtasks, dependencies, or blockers — or is every task standalone?

**Decision:** All tasks are standalone. No subtasks, dependencies, or blocker relationships at launch.

**Rationale:** Task relationships add significant data model complexity, UI complexity (dependency visualization, cycle detection, cascade behavior), and conceptual overhead. The BRD scope boundaries (Decision 011) deliberately exclude project planning features like dependencies. Teams can use comments to reference related tasks informally. The data model can be extended to support relationships in the future without breaking changes.
