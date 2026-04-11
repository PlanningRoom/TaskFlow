# Decision 010: Mobile Navigation Pattern

**Status:** Decided

**Category:** Layout & Navigation

**Question:** The PRD specifies the sidebar becomes a hamburger menu on mobile. Should it be a slide-out hamburger sidebar, a bottom tab bar, or another pattern? How do users access key areas (dashboard, projects, notifications) on small screens?

**Decision:** Slide-out hamburger sidebar on mobile. Tapping the hamburger icon in the top-left of the header slides the full sidebar in from the left as an overlay with a dimmed backdrop. The sidebar content and hierarchy match the desktop sidebar. Tapping the backdrop or a navigation item closes the sidebar.

**Rationale:** A slide-out sidebar keeps the mobile navigation consistent with desktop — same items, same order, same mental model. A bottom tab bar was considered but would require selecting only 4–5 top-level items and hiding the project list, which is a core navigation target. The hamburger pattern aligns with what the PRD already specifies and is well understood by users. The dimmed backdrop provides a clear affordance for dismissal.
