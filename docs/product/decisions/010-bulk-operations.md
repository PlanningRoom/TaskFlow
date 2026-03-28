# Decision 010: Bulk Operations

**Status:** Decided

**Category:** Task Features

**Question:** Can users select multiple tasks and perform actions in bulk — such as changing status, reassigning, applying labels, or cancelling — or are all task actions single-task only?

**Decision:** No bulk operations at launch. All task actions are performed on individual tasks.

**Rationale:** Bulk operations add significant UI complexity — multi-select behavior, a contextual action bar, confirmation dialogs, and error handling for partial failures. For teams of 10–50 users working on typical project sizes, single-task actions are sufficient. Bulk operations can be added as a productivity enhancement in a future iteration once core workflows are proven.
