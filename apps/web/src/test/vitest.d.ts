import type { AxeMatchers } from 'vitest-axe/matchers';
import 'vitest';

// Vitest 3 exposes assertion types via the `vitest` module (not the legacy `Vi`
// global namespace that vitest-axe/extend-expect targets), so augment it here.
// Runtime registration happens in src/test/setup.ts via expect.extend.
declare module 'vitest' {
  // biome-ignore lint/suspicious/noExplicitAny: mirrors vitest-axe's own signature
  interface Assertion<T = any> extends AxeMatchers {}
  interface AsymmetricMatchersContaining extends AxeMatchers {}
}
