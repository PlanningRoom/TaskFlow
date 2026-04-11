# Decision 024: Filter UI Pattern

**Status:** Decided

**Category:** Search & Filtering UX

**Question:** How should project-level filters be presented — a toolbar with dropdown selectors, a filter bar with removable chips, a collapsible filter panel, or a combination? How are active filters indicated and cleared?

**Decision:** A filter toolbar with dropdown selectors, with active filters displayed as removable chips below the toolbar. The toolbar sits in the project sub-navigation area (below the header, above the board/list content) and contains:

- A "Filter" button that reveals filter dropdowns (Status, Assignee, Priority, Label, Due Date)
- A sort control dropdown
- A view toggle (Board / List)

When filters are active, a row of chips appears below the toolbar showing each active filter (e.g., "Status: In Progress", "Assignee: Sarah"). Each chip has an × to remove it, and a "Clear all" link appears at the end.

**Rationale:** The toolbar + chips pattern provides both compact access (filters collapse behind a button when not in use) and clear visibility (active filters are always visible as chips, so users don't forget they're filtering). Removable chips make it easy to adjust individual filters without reopening the dropdown. This pattern is used by most modern project management tools and matches user expectations. Keeping filters in the project sub-nav ensures they're always accessible without competing with the global header.
