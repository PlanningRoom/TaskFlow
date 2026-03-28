# Decision 006: Priority Levels

**Status:** Decided

**Category:** Task Features

**Question:** Should tasks have a dedicated priority field (e.g., Low, Medium, High, Urgent), or is priority handled through labels/tags?

**Decision:** Tasks have a dedicated priority field with fixed levels: None, Low, Medium, High, and Urgent. Priority is separate from labels/tags.

**Rationale:** The BRD lists priority as a must-have task field. A dedicated field is better than overloading labels because it enables consistent sorting and filtering by priority across all projects. Fixed levels keep it simple — no configuration needed. "None" is the default so priority is optional and doesn't force users to triage every task up front.
