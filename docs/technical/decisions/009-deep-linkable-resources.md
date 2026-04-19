# Decision 009: Deep-Linkable Resources

**Status:** Decided

**Category:** Platform & Topology

**Question:** Which application states are deep-linkable via URL?

**Decision:** Projects, board/list view selection, and individual tasks are all addressable by URL. Task URLs follow `/projects/:projectId/tasks/:taskId` (PRD §10.3). Loading a task URL opens the project view with the task detail panel open.

**Rationale:** Inherited from PRD §10.3. Deep links are required for notification click-through, search result navigation, and sharing. This constrains the frontend routing design (Decision 055) — routes must support parallel panel state layered on the underlying page.
