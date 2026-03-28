# Decision 021: Activity Feed Scope

**Status:** Decided

**Category:** Dashboard & Activity

**Question:** Is the activity feed available at the workspace level, the project level, or both? Does it also appear on individual tasks as a history log?

**Decision:** The activity feed is available at two levels:

1. **Dashboard (workspace-wide)** — shows recent activity across all projects the user has access to. This is one of the three dashboard sections (Decision 020).
2. **Project level** — each project has its own activity feed showing changes within that project only.

Individual tasks do not have a dedicated activity/history log. Comments on a task serve as the task-level record of discussion and decisions.

**Rationale:** A workspace-wide feed on the dashboard lets users catch up on everything at once, while a project-level feed lets users focus on a specific body of work — both are natural and expected. A task-level history log (tracking every field change) adds data model complexity and storage overhead for marginal value — comments already capture the meaningful narrative of what happened and why. Task history can be added later if users need detailed audit trails.
