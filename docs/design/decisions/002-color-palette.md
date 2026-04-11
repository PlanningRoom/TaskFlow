# Decision 002: Color Palette

**Status:** Decided

**Category:** Visual Identity & Brand

**Question:** What are the primary, secondary, accent, and semantic (success, warning, error, info) colors for TaskFlow? This includes defining the fixed label color palette referenced in the PRD.

**Decision:** Warm neutral gray base with Ocean Teal (`#0d9488`) as the primary accent color. The palette is:

- **Base:** Warm grays with a slight warm undertone (e.g., `#faf9f7` app background, `#f5f3ef` surfaces, `#2c2418` primary text)
- **Primary accent:** Ocean Teal (`#0d9488`) for interactive elements — buttons, links, selected states, focus rings. Hover: `#0f766e`.
- **Semantic colors:** Green (`#22c55e`) for success/Done, amber (`#f59e0b`) for warning/approaching due, red (`#ef4444`) for error/overdue/Urgent, blue (`#3b82f6`) for informational
- **Surface hierarchy:** White (`#ffffff`) cards → warm light gray (`#f5f3ef`) surfaces → warm off-white (`#faf9f7`) app background. Warm-tinted shadows using `rgba(120,100,70,...)`.
- **Label palette:** A fixed set of 8 colors (blue, green, red, purple, amber, pink, cyan, orange) designed for WCAG AA contrast with white text.

**Rationale:** Ocean Teal is professional, calming, and clearly distinct from the semantic colors (green/amber/red/blue), avoiding confusion between interactive elements and status indicators. The warm neutral base avoids the clinical feel of pure grays, creating a grounded and approachable workspace. Warm-tinted shadows reinforce the warmth at a subtle level. The design option (Warm Neutral) and color palette (Ocean Teal) were selected from three mockup variations after evaluating the visual direction.
