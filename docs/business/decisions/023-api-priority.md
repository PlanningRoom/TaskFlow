# Decision 023: API Priority

**Status:** Decided

**Category:** Integration Strategy

**Question:** Is providing a public API for third-party integrations a priority for the initial release?

**Decision:** Internal API only, designed to be opened later. No public API at launch, but the internal API will be clean and well-structured to make future public exposure straightforward.

**Rationale:** No integrations (Decision 022) means no external consumers need API access now. The frontend will use an internal API regardless, so good design is already a best practice. Adding public-facing concerns (API key auth, documentation, rate limiting) can be done incrementally later without rearchitecting.
