# Decision 025: Motion & Reduced-Motion Support

**Status:** Decided

**Category:** Design System Foundations

**Question:** What is the motion policy, and how do we support users who prefer reduced motion?

**Decision:** Transitions are short (120–200ms) for hovers, focus rings, panel slides, modal appearances, and toast appearance (DRD §13.1). When `prefers-reduced-motion: reduce` is active, all transitions are replaced with instant state changes (0ms).

**Rationale:** Inherited from DRD §13.2 and Design Decision 014. Required for WCAG 2.1 AA compliance (Decision 017). Implementation is a single `@media (prefers-reduced-motion: reduce)` block that zeros out transition durations globally.
