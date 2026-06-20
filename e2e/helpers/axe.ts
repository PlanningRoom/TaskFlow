import AxeBuilder from '@axe-core/playwright';
import { expect, type Page } from '@playwright/test';

/**
 * Rule ids excluded from the automated E2E sweep. These are the "use of colour"
 * checks (contrast + colour-only links) that Phase H4 explicitly routed to the
 * *manual* a11y pass (apps/web/docs/a11y-manual-checklist.md), mirroring the
 * jsdom component-test convention in apps/web/src/test/axe.ts (which disables
 * `color-contrast`). Everything structural — roles, names, labels, landmarks,
 * ARIA, focus order — stays enforced on every visited page (ADR 081).
 *
 * Filtered out of the results (rather than passed to `disableRules`) so an
 * experimental id like `link-in-text-block-style`, which isn't always a
 * registered rule, never throws "unknown rule".
 */
const MANUALLY_REVIEWED_RULES = new Set([
  'color-contrast',
  'link-in-text-block',
  'link-in-text-block-style',
]);

/**
 * Run axe-core against the current page and assert no blocking violations
 * (ADR 081 — an accessibility check on every visited page). Scoped to WCAG
 * 2.0/2.1 A + AA. Pass `ignoreRules` to drop an additional, triaged id —
 * document why at the call site.
 */
export async function expectNoA11yViolations(
  page: Page,
  options: { ignoreRules?: string[] } = {},
): Promise<void> {
  const ignored = new Set([...MANUALLY_REVIEWED_RULES, ...(options.ignoreRules ?? [])]);
  const { violations } = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();

  const blocking = violations.filter((v) => !ignored.has(v.id));
  const summary = blocking
    .map((v) => `  • ${v.id} (${v.impact}): ${v.nodes.length} node(s) — ${v.help}`)
    .join('\n');
  expect(blocking, `Accessibility violations found:\n${summary}`).toEqual([]);
}
