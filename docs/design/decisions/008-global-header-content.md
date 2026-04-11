# Decision 008: Global Header Content

**Status:** Decided

**Category:** Layout & Navigation

**Question:** What elements live in the persistent top header bar? Candidates include: search, notifications bell, user avatar/menu, breadcrumbs, and page title. What is included and how are they arranged?

**Decision:** The global header contains:

- **Left:** Page title or breadcrumb trail (e.g., "Dashboard" or "Projects / Marketing / Board")
- **Center-right:** Global search input
- **Right:** Notifications bell icon (with unread badge), user avatar (clicking opens a dropdown with profile settings and sign out)

The header is a slim, single-row bar that does not compete with the sidebar for navigation. On mobile, the left side shows a hamburger menu icon replacing the sidebar.

**Rationale:** The header serves as a utility bar — orientation (breadcrumbs), quick access (search), and status (notifications). Keeping it slim preserves vertical space for task content. Breadcrumbs provide context for where the user is without relying on the sidebar being visible. Search in the header makes it accessible from every page, matching the PRD requirement. The user avatar dropdown is a standard pattern that keeps profile/settings access one click away without cluttering the header.
