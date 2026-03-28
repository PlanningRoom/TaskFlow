# Decision 020: Dashboard Layout

**Status:** Decided

**Category:** Dashboard & Activity

**Question:** What sections make up the user dashboard — assigned tasks only, or also summary statistics, project status overviews, recent activity, and/or upcoming due dates?

**Decision:** The dashboard has three sections:

1. **My Tasks** — tasks assigned to the current user, grouped by project, showing status, priority, and due date. Overdue tasks are visually highlighted.
2. **Recent Activity** — a feed of recent changes across all projects the user has access to (status changes, new comments, new tasks, assignments).
3. **Projects** — a list of projects the user has access to, each showing a summary of task counts by status.

**Rationale:** These three sections answer the questions a user has when they open the app: "What should I be working on?" (My Tasks), "What's been happening?" (Recent Activity), and "How are things going overall?" (Projects). This aligns with BRD requirement SF-03, which specifies assigned tasks, recent activity, and project statuses. The layout is informative without introducing summary statistics or charts, which would push toward reporting — a feature explicitly out of scope.
