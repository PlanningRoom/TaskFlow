# Decision 015: Board Interaction Model

**Status:** Decided

**Category:** Board & Views

**Question:** How do users move tasks between statuses on the board — drag-and-drop between columns, a status dropdown/menu on the task, or both?

**Decision:** Both drag-and-drop and a status dropdown. Drag-and-drop is the primary interaction on desktop for moving tasks between status columns. A status dropdown on the task detail view (and optionally on the card) provides an alternative method. The list view (Decision 017) uses the dropdown exclusively.

**Rationale:** Drag-and-drop is the expected interaction for kanban-style boards — it's intuitive and efficient for desktop users. However, the BRD requires accessible alternatives (AC-05), and drag-and-drop is problematic for keyboard-only users, screen reader users, and mobile users. A status dropdown ensures all users can change task status regardless of input method. Supporting both means the board feels natural on desktop while remaining fully accessible.
