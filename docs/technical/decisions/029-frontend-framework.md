# Decision 029: Frontend Framework

**Status:** Decided

**Category:** Stack Foundations

**Question:** Which UI framework renders the TaskFlow client?

**Options considered:**
- React (with Vite)
- Vue
- Svelte / SvelteKit
- SolidJS
- Next.js / Remix (React-based, full-stack)

**Decision:** React 18+, rendered as a standalone SPA by Vite (Decision 031).

**Rationale:** With a Python/FastAPI backend (Decisions 028/032), a full-stack framework like Next.js or Remix is a mismatch — those are Node-server-based. A plain SPA that calls the FastAPI API is the clean fit. React has the deepest ecosystem for the specific libraries we need: Radix UI (Decision 058), dnd-kit (Decision 059), TanStack Query/Router (Decisions 053/055), react-markdown (Decision 060), react-intl (Decision 061). A demo project benefits from that library depth.
