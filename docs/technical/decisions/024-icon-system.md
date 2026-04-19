# Decision 024: Icon System

**Status:** Decided

**Category:** Design System Foundations

**Question:** Which icon library does TaskFlow use?

**Decision:** Lucide — open source, outlined style. Icons are used at 18–20px standard, 13–16px compact, and 15px in the search input, with stroke width 1.75–2px.

**Rationale:** Inherited from DRD §4.1 and Design Decision 005. Lucide is comprehensive, open source, and ships per-icon components for tree-shaking in any framework. Color inherits from parent text except for semantic (status/priority) icons.
