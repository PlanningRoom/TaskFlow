# Decision 018: Status Color Mapping

**Status:** Decided

**Category:** Board & Task Design

**Question:** What color represents each task status (Backlog, To Do, In Progress, In Review, Done, Cancelled)? These colors appear on board column headers, status badges, and task cards.

**Decision:** Status colors use intuitive, widely recognized associations:

| Status | Color | Reasoning |
|--------|-------|-----------|
| **Backlog** | Gray | Inactive, not yet planned — visually recedes |
| **To Do** | Blue | Ready and waiting — calm, informational |
| **In Progress** | Amber/Yellow | Active work — draws attention, implies motion |
| **In Review** | Purple | Distinct from In Progress, suggests a different phase |
| **Done** | Green | Universal "complete" signal |
| **Cancelled** | Muted red/rose | Terminated — clearly distinct from active statuses but not alarming |

Colors appear as column header indicators, status badges on cards, and status dropdown options. Each color has a soft/muted variant for backgrounds and a stronger variant for text/icons to ensure contrast.

**Rationale:** These mappings leverage existing user expectations — green for done, amber for active, gray for inactive. Purple for In Review provides clear differentiation from In Progress (amber) without using a color that conflicts with semantic meanings. Muted red for Cancelled distinguishes it from error states (which use a brighter red) while clearly signaling termination. The soft/strong variant approach ensures accessibility across different contexts.
