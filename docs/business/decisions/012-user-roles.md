# Decision 012: User Roles

**Status:** Decided

**Category:** User Roles & Access

**Question:** What user roles will exist in TaskFlow (e.g., admin, manager, contributor, viewer)?

**Decision:** Four roles: Owner, Admin, Member, Viewer.
- **Owner:** Account creator with full control over the workspace.
- **Admin:** Manages day-to-day operations, invites users, configures settings.
- **Member:** Creates, edits, and manages tasks and projects.
- **Viewer:** Read-only access for stakeholders or external collaborators.

**Rationale:** The invite-only model means external collaborators may need read-only access. A clear ownership model prevents ambiguity about ultimate control, while delegating admin duties keeps things manageable for medium teams.
