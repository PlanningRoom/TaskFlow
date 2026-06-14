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

---

**Amendment (2026-06-14, Phase H3):** the **toast queue is implemented with React Context** (`ToastProvider` + `useToast`, Radix-backed), not Zustand. A working Context-based toast already existed from Part G and covers every call site; the standardized mutation-error toast is wired through a small module→context bridge off the TanStack Query `MutationCache`. Migrating it to Zustand would have been churn with no functional gain, so Context was retained. Zustand remains the chosen store for **future** global UI that genuinely needs a store outside the React tree (e.g. a command menu), which is not yet built. This amendment supersedes the "global toast queue → Zustand" example in the decision above; the principle (Zustand for cross-cutting UI state that needs a store, Context for the rest) is unchanged.
