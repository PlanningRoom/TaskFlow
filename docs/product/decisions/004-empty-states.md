# Decision 004: Empty States

**Status:** Decided

**Category:** Authentication & Onboarding

**Question:** What do users see when a project has no tasks, the dashboard has no activity, or a search returns no results — blank screens, helpful prompts, or illustrative placeholders?

**Decision:** Text prompts with a call to action. Each empty state displays a short contextual message explaining why the area is empty and guides the user to the next action (e.g., "No tasks yet — create your first one" with a button). Key empty states include: dashboard (no tasks/activity), project board (no tasks), individual status columns, search results, filter results, notifications, and the activity feed. Prompts are role-aware — Viewers see informational messages rather than action prompts for things they cannot do. Empty status columns receive lighter treatment (subtle hint text) than fully empty pages.

**Rationale:** Text prompts with calls to action are lightweight to implement, require no illustration assets or design dependencies, and communicate clearly. This approach aligns with the first-run experience (Decision 003) — the empty states and first-run contextual prompts share the same implementation. Illustrations can be layered on later without changing the underlying approach if the visual design matures.
