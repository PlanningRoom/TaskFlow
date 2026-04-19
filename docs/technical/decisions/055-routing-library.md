# Decision 055: Routing Library

**Status:** Decided

**Category:** Client Architecture

**Question:** Which library handles client-side routing?

**Options considered:**
- TanStack Router
- React Router v6/v7
- wouter

**Decision:** TanStack Router v1.

- Fully type-safe routes and search params.
- Search params drive board/list filter state (shared across views, preserved on navigation per PRD §12.2 and §9.3).
- Task detail panel (PRD §10) is modeled as a nested route under the project view (`/projects/:projectId/tasks/:taskId`) — overlays on top of the same parent route output.
- Notification navigation, search result clicks, and activity feed links all just navigate to the task route and trust the router to render the panel.

**Rationale:** Type-safe search params directly benefit TaskFlow's filter model (every filter dimension is URL-backed). TanStack Router's nested routing with parallel panel output matches Decision 009 and PRD §10.3 cleanly. React Router is a safe fallback but trails on search-param type safety.
