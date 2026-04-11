# Decision 009: Navigation Model

**Status:** Decided

**Category:** Layout & Navigation

**Question:** How do users navigate between major areas (dashboard, projects, settings, notifications)? Is navigation primarily sidebar-driven, top-nav with tabs, or a combination? How does the user move from the dashboard to a project board to task detail?

**Decision:** Sidebar-driven navigation. The sidebar is the primary navigation mechanism, providing direct access to the dashboard, notifications, and individual projects. Within a project, a secondary navigation bar below the header provides view switching (Board / List) and project-level controls (filters, sort, project settings). Settings pages use their own sidebar sub-navigation or tabbed layout within the settings area.

**Rationale:** Sidebar navigation is the dominant pattern for project management tools and multi-project workspaces. It keeps the project list always visible on desktop, allowing fast switching without navigating back to an index page. The two-level approach (sidebar for app navigation, sub-nav for project views) creates a clear hierarchy: the sidebar answers "where in the app am I?" and the project sub-nav answers "how am I viewing this project?"
