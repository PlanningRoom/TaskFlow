# Decision 054: Client State Management

**Status:** Decided

**Category:** Client Architecture

**Question:** How is non-server client state managed?

**Options considered:**
- Component-local state + React Context
- Zustand
- Jotai / Recoil
- Redux / Redux Toolkit

**Decision:** Zustand for cross-cutting UI state (e.g., global toast queue, command-menu open state). React Context for auth/user state (current user, permissions). All filter, selected-task, and active-view state lives in the URL and is owned by the router (Decision 055), not a store.

**Rationale:** Most of what would traditionally be "client state" is either server state (Decision 053) or URL state. What remains is small; Zustand is the minimal store with good TypeScript ergonomics. Redux is overkill.
