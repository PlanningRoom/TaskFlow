# Decision 057: CSS Strategy

**Status:** Decided

**Category:** Client Architecture

**Question:** How are styles authored and scoped?

**Options considered:**
- Tailwind CSS atop the design-token CSS custom properties
- Vanilla CSS with CSS Modules
- CSS-in-JS (styled-components, Emotion, vanilla-extract)
- PandaCSS / UnoCSS

**Decision:** Tailwind CSS v3 configured to consume the CSS custom property token layer from Decision 022.

- `:root` declares all tokens (from DRD §2) as CSS custom properties in a single `src/styles/tokens.css` file.
- `tailwind.config.ts` maps Tailwind's theme to those properties: `theme.colors.primary = 'var(--primary)'`, `theme.spacing` maps to the 4px-scale token values, etc.
- RTL readiness (Decision 019) uses Tailwind logical-property utilities (`ms-*`, `me-*`, `ps-*`, `pe-*`, `start-*`, `end-*`).
- Reduced-motion (Decision 025) applied globally via a `@media (prefers-reduced-motion: reduce) { * { transition-duration: 0ms !important; animation-duration: 0ms !important; } }` rule.

**Rationale:** Tailwind accelerates layout work; the custom-property bridge keeps DRD §2 authoritative — a future theming change (e.g., dark mode) swaps token values, not component code. Logical properties are first-class in Tailwind as of v3.3.
