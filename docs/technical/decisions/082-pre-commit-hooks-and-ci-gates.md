# Decision 082: Pre-Commit Hooks & CI Gates

**Status:** Decided

**Category:** Quality & Workflow

**Question:** Which checks block a commit, push, or merge?

**Options considered:**
- Pre-commit only
- CI only
- Both

**Decision:** Both — cheap checks local, full checks in CI.

**Pre-commit (local, on staged files only, must run in <5 seconds):**
- Husky + lint-staged for frontend — Biome format and lint on staged `.ts/.tsx`.
- `pre-commit` framework (Python) for backend — Ruff format and lint on staged `.py`.
- Secret scan (`detect-secrets` or similar) on staged content.

**CI on every PR (blocking merge to main):**
- Type-check (frontend `tsc --noEmit`, backend `mypy` or Pyright).
- Lint (Biome, Ruff).
- Unit tests (Vitest, pytest).
- Integration tests (pytest against ephemeral Postgres).
- Playwright smoke (Decision 080).
- axe-core accessibility checks (Decision 081).
- Dependabot alerts reviewed (Decision 086).

**Merge to main triggers deploy** (Decision 071).

**Rationale:** Fast local checks catch the 80% of style and obvious-bug issues before they hit CI, making CI runs meaningful. CI is the ground truth — local hooks can be skipped, CI cannot.
