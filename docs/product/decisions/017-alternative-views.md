# Decision 017: Alternative Views

**Status:** Decided

**Category:** Board & Views

**Question:** Beyond the board view, what alternative views are available — a list/table view, a calendar view, or others? Is the list view only for accessibility, or a general-purpose option available to all users?

**Decision:** A list/table view is available as a general-purpose alternative to the board view, accessible to all users. It displays tasks in a tabular format with sortable columns (title, status, assignee, priority, due date, labels). No calendar view at launch.

**Rationale:** The BRD requires accessible alternatives for complex interaction patterns like the task board (AC-05). A list view fulfills this requirement while also serving users who simply prefer tabular data — making it general-purpose rather than accessibility-only means it gets proper design attention and benefits everyone. Sortable columns give the list view unique utility that the board doesn't offer. A calendar view adds significant implementation complexity and is less essential given that TaskFlow is status-focused rather than schedule-focused.
