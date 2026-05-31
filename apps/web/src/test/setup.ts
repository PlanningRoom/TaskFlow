import '@testing-library/jest-dom/vitest';
import { expect } from 'vitest';
import * as axeMatchers from 'vitest-axe/matchers';

// Register the axe accessibility matcher (`toHaveNoViolations`) at runtime so
// every component test can assert on it (ADR 081).
expect.extend(axeMatchers);
