import { fileURLToPath, URL } from 'node:url';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  resolve: {
    // Mirror the `@/*` -> `src/*` path alias from tsconfig.json so the dev
    // server resolves it (Vite does not read tsconfig `paths` on its own; the
    // Rolldown production build does, but dev import-analysis does not).
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
});
