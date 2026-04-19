# Decision 013: Public API Exposure

**Status:** Decided

**Category:** External Surface

**Question:** Do we expose a public API at launch?

**Decision:** No public API. Only an internal API used by the TaskFlow web client. The internal API is designed to be clean and coherent so it could be exposed publicly in the future.

**Rationale:** Inherited from BRD IA-02 / IA-03 and Business Decision 023. A public API implies versioning guarantees, rate limiting for untrusted callers, API keys, and documentation — all deferred. The internal API should still be designed as if it could be public (stable resource shapes, clear error contract).
