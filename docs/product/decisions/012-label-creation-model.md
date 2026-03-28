# Decision 012: Label Creation Model

**Status:** Decided

**Category:** Labels & Tags

**Question:** Are labels pre-defined by admins, or can any member create labels on the fly when tagging a task?

**Decision:** Labels are admin-managed. Owners and Admins create, edit, and delete labels. Members select from the existing label set when tagging tasks.

**Rationale:** Admin-managed labels prevent label sprawl — without governance, teams quickly end up with duplicates ("bug", "Bug", "bugs") and inconsistent naming. Since TaskFlow already has a clear role hierarchy, leveraging Admins as label managers is natural and requires no new concepts. The label set stays clean and meaningful, which makes filtering by label reliable.
