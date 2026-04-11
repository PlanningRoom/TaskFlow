# Decision 005: Iconography Style

**Status:** Decided

**Category:** Visual Identity & Brand

**Question:** What icon library and style should TaskFlow use — outlined vs filled, rounded vs sharp? Options include Lucide, Heroicons, Material Symbols, Phosphor, and others.

**Decision:** Lucide icons, outlined style with 1.5px stroke weight at the default 24px size. Icons are rendered at 20px for inline/UI use and 16px for compact contexts (task cards, table rows).

**Rationale:** Lucide is open source, actively maintained, and has excellent coverage for project management concepts (tasks, users, settings, search, notifications, drag handles, statuses). The outlined style matches the minimal & soft modern personality — lighter and more refined than filled icons. Lucide's consistent stroke weight and geometry pair well with Inter. The library also has good tree-shaking support for keeping bundle size small.
