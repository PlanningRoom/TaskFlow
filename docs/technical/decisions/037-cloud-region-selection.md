# Decision 037: Cloud Region Selection

**Status:** Decided

**Category:** Stack Foundations

**Question:** Which specific AWS region hosts TaskFlow?

**Options considered:**
- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)

**Decision:** `us-east-1` (N. Virginia).

**Rationale:** Cheapest AWS region, largest service coverage, default for most AWS tooling. Documented in the privacy policy per BRD DI-03. Users are assumed to be predominantly North American or globally distributed for a demo project; EU-only hosting would trade cost for a GDPR-posture benefit that TaskFlow's minimal data collection (Decision 021) does not need.
