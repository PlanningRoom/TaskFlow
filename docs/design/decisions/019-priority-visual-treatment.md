# Decision 019: Priority Visual Treatment

**Status:** Decided

**Category:** Board & Task Design

**Question:** How should priority levels (None, Low, Medium, High, Urgent) be visually represented on task cards and in the task detail panel? Options include colored dots, flag icons, arrow icons, text badges, or a combination.

**Decision:** Priority is displayed as a small colored icon using directional indicators:

| Priority | Icon | Color |
|----------|------|-------|
| **Urgent** | Double up arrow (⇈) or alert triangle | Red |
| **High** | Single up arrow | Orange |
| **Medium** | Horizontal bar / equals | Amber/Yellow |
| **Low** | Single down arrow | Blue |
| **None** | No icon displayed | — |

On task cards, the priority icon appears in the bottom-left metadata row. In the task detail panel, the priority selector shows the icon alongside the level name. In the list view, the icon appears in the priority column.

**Rationale:** Directional arrows communicate relative importance intuitively — up means higher priority, down means lower. Color reinforces the hierarchy (red = urgent, cooling down to blue = low) without relying on color alone, satisfying the WCAG requirement that information not be conveyed by color only. Hiding the icon for "None" keeps cards clean when priority is unset, which is the default state. This pattern is used by Linear and other modern tools and is familiar to the target audience.
