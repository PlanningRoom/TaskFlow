# Decision 081: Accessibility Testing

**Status:** Decided

**Category:** Quality & Workflow

**Question:** How is WCAG 2.1 AA compliance validated?

**Options considered:**
- `@axe-core/playwright` in E2E
- `vitest-axe` in component tests
- Storybook + a11y addon
- Manual audits only
- Combination

**Decision:** Three layers:

1. **Automated in E2E (Decision 080):** `@axe-core/playwright` runs a full `axe.run()` on every page visited by the Playwright smoke tests. Any `violations` array non-empty fails the test.
2. **Automated in component tests:** `vitest-axe` invoked on critical components — all modals, forms, the task detail panel, menus, the board drag-and-drop surface.
3. **Manual at release checkpoints:** keyboard-only navigation of every user journey (PRD §6), a pass with VoiceOver or NVDA, contrast spot-checks.

The design-token palette (DRD §2) is pre-validated for AA contrast; the risk is regressions introduced by new components using off-palette values.

**Rationale:** Automated axe catches ~30–40% of real issues but is a strong regression gate. Manual testing catches the other majority. Keyboard operability and screen-reader semantics are hard constraints from Decision 017.
