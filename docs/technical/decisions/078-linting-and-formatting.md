# Decision 078: Linting & Formatting

**Status:** Decided

**Category:** Quality & Workflow

**Question:** Which tools enforce code style and catch common mistakes?

**Options considered:**
- ESLint + Prettier (frontend) + Ruff + Black (backend)
- Biome (frontend) + Ruff (backend)
- Language-native only

**Decision:**
- **Frontend (TypeScript/React):** Biome — single tool for both linting and formatting. Rust-based, fast, sensible defaults.
- **Backend (Python):** Ruff — single tool for both linting and formatting (Ruff's formatter is Black-compatible).

Configs:
- `biome.json` at the monorepo root, targets `apps/web/**/*.{ts,tsx}` and shared packages.
- `pyproject.toml` `[tool.ruff]` section in `apps/api/`.

Both tools run in CI (Decision 082) and via pre-commit hooks on staged files.

**Rationale:** Biome and Ruff each consolidate what used to be two tools (linter + formatter), cutting config complexity in half. Both are materially faster than the legacy ESLint+Prettier and Pylint+Black stacks, which matters for pre-commit ergonomics. Biome's ESLint-plugin coverage is now adequate for a React + TS app; specific gaps (e.g., React-hooks-exhaustive-deps, jsx-a11y) are covered by its built-in rule sets.
