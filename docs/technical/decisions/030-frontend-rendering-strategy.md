# Decision 030: Frontend Rendering Strategy

**Status:** Decided

**Category:** Stack Foundations

**Question:** How are pages rendered — SPA, SSR, or hybrid?

**Options considered:**
- Pure SPA (client-side rendering)
- Full SSR
- Hybrid (SSR for initial load, client-side for navigation)

**Decision:** Pure SPA. A static HTML shell is served by nginx; React hydrates and handles all subsequent rendering client-side.

**Rationale:** TaskFlow is entirely an authenticated application with no SEO-relevant content. SSR would require a Node server in addition to the Python backend, adding a moving part for no user-facing benefit. A static build + SPA fits the EC2 t4g.small footprint (Decision 036) — nginx serves `index.html` + hashed assets. The initial-paint penalty versus SSR is unimportant for a logged-in dashboard app.
