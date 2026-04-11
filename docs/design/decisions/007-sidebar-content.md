# Decision 007: Sidebar Content & Hierarchy

**Status:** Decided

**Category:** Layout & Navigation

**Question:** What items appear in the sidebar and in what order? Candidates include: workspace name, navigation links (dashboard, projects, settings), project list, labels, and member list. How are these grouped and prioritized?

**Decision:** The sidebar is organized top-to-bottom as follows:

1. **Logo/wordmark** — workspace identity at the top
2. **Primary navigation** — Dashboard, Notifications
3. **Projects section** — "Projects" heading with a list of projects the user has access to, plus a "New Project" action for users with create permission
4. **Bottom section** (pinned to bottom) — Settings link, user avatar with name and role

Labels and member management are accessed through Settings, not the sidebar directly.

**Rationale:** This keeps the sidebar focused on daily navigation — the things users click most often (dashboard, their projects). Putting notifications in the sidebar gives it a persistent home alongside the header bell icon. Pinning the user profile and settings to the bottom follows a well-established convention (VS Code, Slack, Discord). Keeping labels and members out of the sidebar avoids clutter — these are administrative functions, not daily navigation targets.
