import '@testing-library/jest-dom/vitest';
import { expect } from 'vitest';
import * as axeMatchers from 'vitest-axe/matchers';

// Register the axe accessibility matcher (`toHaveNoViolations`) at runtime so
// every component test can assert on it (ADR 081).
expect.extend(axeMatchers);

// jsdom doesn't implement the Pointer Capture API that several Radix primitives
// (Toast swipe, Select, Slider) call on pointer events. Provide no-op shims so
// interaction tests don't throw `hasPointerCapture is not a function`.
if (typeof Element !== 'undefined' && !Element.prototype.hasPointerCapture) {
  Element.prototype.hasPointerCapture = () => false;
  Element.prototype.setPointerCapture = () => {};
  Element.prototype.releasePointerCapture = () => {};
}
