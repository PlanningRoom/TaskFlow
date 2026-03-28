# Decision 011: Task Ordering Within Columns

**Status:** Decided

**Category:** Task Features

**Question:** How are tasks ordered within a status column — by creation date, by a sort field (priority, due date, assignee), by manual drag-and-drop reordering, or some combination?

**Decision:** Tasks are sorted by creation date (newest at top) by default, with the ability to sort by priority, due date, or assignee. No manual drag-and-drop reordering within columns.

**Rationale:** Manual reordering within columns requires persistent position tracking for every task, which adds data model complexity and conflict potential in real-time collaborative environments (two users reordering the same column simultaneously). Sort-based ordering is simpler to implement, predictable, and gives users flexibility through sort options. Sorting by priority or due date covers the most common need — surfacing the most important or urgent work first.
