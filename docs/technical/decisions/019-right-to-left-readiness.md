# Decision 019: Right-to-Left Readiness

**Status:** Decided

**Category:** Cross-Cutting Concerns

**Question:** Does the application support RTL languages, and how?

**Decision:** RTL is not supported at launch, but the CSS is written to be RTL-ready. All directional styling uses CSS logical properties (`margin-inline-start`, `padding-inline-end`, `inset-inline-start`, etc.) rather than physical properties (`margin-left`, `padding-right`).

**Rationale:** Inherited from BRD IL-03 and Business Decision 029. Using logical properties is nearly free at build time — no special tooling required — and makes adding Arabic/Hebrew later a configuration change rather than a rewrite.
