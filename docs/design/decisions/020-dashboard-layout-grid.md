# Decision 020: Dashboard Layout Grid

**Status:** Decided

**Category:** Dashboard & Feed Design

**Question:** The PRD defines three dashboard sections (My Tasks, Recent Activity, Projects). How should these be arranged — side-by-side columns, stacked rows, a mixed grid, or a different layout? How does the layout adapt across breakpoints?

**Decision:** A two-column layout on desktop with a stacked single-column layout on mobile:

- **Desktop (1024px+):** Left column (~60%) contains "My Tasks" (the primary section, grouped by project). Right column (~40%) contains "Recent Activity" at the top and "Projects" below.
- **Tablet (768–1023px):** Same two-column layout but with narrower proportions (~55/45).
- **Mobile (<768px):** Single column, stacked: My Tasks → Projects → Recent Activity.

My Tasks is the dominant section because it answers the user's primary question on login: "What do I need to work on?"

**Rationale:** The asymmetric two-column layout gives the most space to the most actionable section (My Tasks) while keeping activity and project overview visible without scrolling on desktop. Stacking on mobile prioritizes My Tasks first and Recent Activity last because the activity feed is informational rather than actionable — on a small screen, what you need to do matters more than what happened recently. This layout adapts naturally across breakpoints without requiring fundamentally different designs.
