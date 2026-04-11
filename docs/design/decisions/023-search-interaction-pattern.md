# Decision 023: Search Interaction Pattern

**Status:** Decided

**Category:** Search & Filtering UX

**Question:** How should global search work visually — a simple search bar in the header with a dropdown results list, or a command-palette style overlay (Cmd+K / Ctrl+K)? How are results displayed and navigated?

**Decision:** A header search bar that expands into a dropdown results list. The search input is always visible in the global header (not hidden behind an icon). When focused or when the user begins typing, a dropdown panel appears below the input showing matching results. Each result shows: task title, project name, and status badge. Selecting a result navigates to the project with the task detail panel open.

A keyboard shortcut (Cmd+K / Ctrl+K) focuses the search input from anywhere in the app.

**Rationale:** An always-visible search bar is more discoverable than a command palette, especially for Viewers and occasional users who may not know keyboard shortcuts. The dropdown-below-input pattern matches the PRD specification ("results appear in a dropdown below the search input as the user types") and is the most widely understood search interaction. Adding Cmd+K as a shortcut gives power users fast access without adding complexity for everyone else. This approach is simpler to implement than a full command palette while covering the PRD's search requirements completely.
