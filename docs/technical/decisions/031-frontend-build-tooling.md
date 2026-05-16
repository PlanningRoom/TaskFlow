# Decision 031: Frontend Build Tooling

**Status:** Decided

**Category:** Stack Foundations

**Question:** Which build toolchain compiles, bundles, and dev-serves the frontend?

**Options considered:**
- Vite
- Next.js / Remix built-in toolchain
- Webpack
- esbuild / tsup directly

**Decision:** Vite 8+.

**Rationale:** Vite is the standard for non-framework React setups in 2026 — instant HMR, fast cold starts, minimal config, TypeScript-native. Framework-native toolchains (Next.js, Remix) are ruled out by Decision 030. Production build outputs hashed static files suitable for nginx to serve directly.
