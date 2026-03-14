# Decision 013: Permission Model

**Status:** Decided

**Category:** User Roles & Access

**Question:** Will there be permission levels or team-based access controls?

**Decision:** Role-based permissions with project-level access controls. Workspace-wide roles (Owner, Admin, Member, Viewer) set the baseline, and project-level access determines which projects each user can see and interact with.

**Rationale:** The invite-only model means external collaborators should only see projects relevant to them, not the entire workspace. Project-level access is manageable complexity for medium teams without requiring team/group-based management or full ACLs.
