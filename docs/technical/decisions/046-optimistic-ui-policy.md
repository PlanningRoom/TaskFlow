# Decision 046: Optimistic UI Policy

**Status:** Decided

**Category:** API & Real-Time

**Question:** Which client actions apply optimistically before the server confirms?

**Options considered:**
- Aggressive (every mutation optimistic)
- Conservative (only low-risk actions)
- None (always wait for server)

**Decision:** Conservative. **Only one action is optimistic: board drag-and-drop (task status change).** Every other mutation — title edit, comment add, label toggle, assignee change, priority, due date — waits for the server response before updating the UI.

**Rationale:** Board drag-and-drop has the highest user-visible latency cost and the cleanest rollback path (the card snaps back). Everything else is a form submit or a property edit where waiting 100–300ms for the round trip is acceptable. Keeping the optimistic surface small avoids complex reconciliation logic against last-write-wins (Decision 008) and the real-time echo (Decision 007). TanStack Query's `onMutate`/`onError`/`onSettled` handles the drag-and-drop rollback.
