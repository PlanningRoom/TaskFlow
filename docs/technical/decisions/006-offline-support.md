# Decision 006: Offline Support

**Status:** Decided

**Category:** Platform & Topology

**Question:** Does TaskFlow support offline use, optimistic local caching, or read-only cached access?

**Decision:** No offline support. An active network connection is required. No service worker, local persistence, or conflict-resolution queue is implemented.

**Rationale:** Inherited from BRD PA-04 and Business Decision 021. Offline introduces substantial complexity (sync engine, conflict resolution beyond last-write-wins, local storage) that a demonstration project does not need. The client may still cache in-memory data within a session.
