import { axe as baseAxe } from 'vitest-axe';

// Derive the options type from vitest-axe's own signature so we don't need a
// direct dependency on axe-core (it's a transitive dep, not resolvable here).
type AxeOptions = NonNullable<Parameters<typeof baseAxe>[1]>;

/**
 * axe configured for jsdom: the `color-contrast` rule is disabled because jsdom
 * has no layout/canvas engine to measure rendered colors (it throws on
 * `getContext`). Contrast is verified against the DRD tokens by design review,
 * not in unit tests. All other WCAG rules run.
 */
export function axe(container: Element, options: AxeOptions = {}) {
  return baseAxe(container, {
    ...options,
    rules: { 'color-contrast': { enabled: false }, ...(options.rules ?? {}) },
  });
}
