# Decision 022: Design Token Layer

**Status:** Decided

**Category:** Design System Foundations

**Question:** How are visual tokens (colors, spacing, typography) expressed in the codebase?

**Decision:** Tokens are declared as CSS custom properties (CSS variables) on `:root`, as defined in DRD §2. Component styles reference tokens rather than hard-coded values.

**Rationale:** Inherited from DRD §2 and Design Decision 002. CSS custom properties are browser-native, work in every framework, and enable future theming (e.g., dark mode) via token value swaps without touching component styles. This choice constrains the CSS strategy (Decision 057) — the token layer must be preserved.
