import { fileURLToPath, URL } from 'node:url';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    css: true,
    coverage: {
      provider: 'v8',
      // Phase H5 gate (DRD-driven): the domain UI under components/ and
      // features/ must stay ≥80% covered. Other dirs (app wiring, generated
      // types, test helpers, i18n catalog) are excluded from the gate.
      include: ['src/components/**', 'src/features/**'],
      exclude: ['**/*.test.{ts,tsx}', '**/index.ts', 'src/components/ui/icons.ts'],
      reporter: ['text-summary', 'html'],
      thresholds: {
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80,
      },
    },
  },
});
