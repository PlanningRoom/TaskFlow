# Decision 015: Board Column Layout

**Status:** Decided

**Category:** Board & Task Design

**Question:** Should board view columns be fixed-width with horizontal scrolling, or fluid-width filling the available viewport? How does this behave as the number of tasks per column grows?

**Decision:** Fixed-width columns (approximately 280–300px each) with horizontal scrolling when columns exceed the viewport width. Each column scrolls vertically independently when its task list exceeds the visible height.

On tablet, columns maintain their fixed width and the board scrolls horizontally. On mobile, as specified in the PRD, columns stack vertically.

**Rationale:** Fixed-width columns ensure consistent card sizing and readability regardless of how many statuses are visible. With 5 active columns at ~290px each (~1450px), the board fits comfortably on standard desktop monitors (1440px+) but scrolls on smaller screens — this is acceptable and expected for Kanban boards. Independent vertical scrolling per column prevents long columns from pushing shorter ones off screen. This is the standard pattern used by Trello, Linear, Asana, and virtually every board-based tool.
