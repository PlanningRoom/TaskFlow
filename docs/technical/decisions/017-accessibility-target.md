# Decision 017: Accessibility Target

**Status:** Decided

**Category:** Cross-Cutting Concerns

**Question:** What accessibility standard does TaskFlow target?

**Decision:** WCAG 2.1 Level AA. All screens and interactions meet AA contrast, keyboard operability, focus visibility, and screen reader compatibility requirements.

**Rationale:** Inherited from BRD AC-01 through AC-05, PRD §16, DRD §14, and Business Decision 026. This constrains every frontend choice — color tokens, component primitives (Decision 058), drag-and-drop (Decision 059), and testing (Decision 081) must all support AA compliance.
