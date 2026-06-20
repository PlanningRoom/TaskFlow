import { fileURLToPath, URL } from 'node:url';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

const proxyTarget = process.env.VITE_PROXY_TARGET ?? 'http://localhost:8000';

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
    // Proxy API + WebSocket to the FastAPI dev server so the SPA can use
    // relative `/api/v1` paths (same-origin) and cookies flow without CORS.
    // The target is overridable via `VITE_PROXY_TARGET`: it stays `localhost`
    // for the host dev workflow, but the docker-compose `web` service sets it to
    // `http://api:8000` so the containerized stack (used by the E2E suite) can
    // reach the API across the compose network.
    proxy: {
      '/api': { target: proxyTarget, changeOrigin: true },
      '/ws': { target: proxyTarget, ws: true, changeOrigin: true },
    },
  },
});
