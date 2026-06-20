import { defineConfig, devices } from '@playwright/test';

/**
 * Phase I1 end-to-end suite (ADR 080 / TDD §16.3). Runs against a seeded
 * `docker compose up` stack: the Vite dev server (:5173) proxies `/api` and
 * `/ws` to the FastAPI app (:8000), so the browser is same-origin and the
 * session + CSRF cookies flow exactly as in production.
 *
 * The suite is serial (`workers: 1`): every journey shares the one seeded
 * "Aurora Studio" workspace, and the real-time/notification journeys assert on
 * cross-context state that parallel runs would race on.
 */
const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:5173';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : [['list']],
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
