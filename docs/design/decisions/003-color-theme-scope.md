# Decision 003: Color Theme Scope

**Status:** Decided

**Category:** Visual Identity & Brand

**Question:** Should TaskFlow support light mode only, dark mode only, or both? This is a scope decision that affects the complexity of the color system and the number of mockups required.

**Decision:** Light mode only at launch. The color system will be implemented using CSS custom properties (design tokens) so that a dark mode can be added later by defining an alternate set of token values without changing component styles.

**Rationale:** Supporting both modes doubles the design and QA effort for colors, contrast checking, and mockups. Light mode is the safer default for a broad audience and the standard for most project management tools. Using CSS custom properties from the start means dark mode is an additive change later — no rearchitecting required. This keeps the initial scope manageable while preserving the option.
