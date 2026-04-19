# Decision 008: Concurrent Edit Conflict Resolution

**Status:** Decided

**Category:** Platform & Topology

**Question:** How do we resolve simultaneous edits to the same task or field by multiple users?

**Decision:** Last-write-wins. The server accepts writes in arrival order; no merging, OT, CRDT, or user-facing conflict prompts are implemented.

**Rationale:** Inherited from PRD §19. Last-write-wins is sufficient for the demonstration scope. Real-time propagation (Decision 007) means losing edits are rare — users see the current state within milliseconds and can re-apply if needed.
