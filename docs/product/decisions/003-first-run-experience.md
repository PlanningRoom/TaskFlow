# Decision 003: First-Run Experience

**Status:** Decided

**Category:** Authentication & Onboarding

**Question:** What do users see after creating a workspace or joining for the first time — a guided setup wizard, a tour, or an empty workspace they populate themselves?

**Decision:** Two approaches based on user type:

- **Owners (new workspace):** The workspace loads normally with contextual prompts in key areas guiding them to create their first project and invite team members. No separate setup wizard.
- **Invited users (joining an existing workspace):** Users land on the dashboard with a brief welcome message orienting them to the workspace and pointing them to projects they have access to. The message goes away once they have assignments and activity.

**Rationale:** Contextual prompts are lighter to build than a wizard and naturally integrate with the normal UI — no separate onboarding flow to maintain. They guide without constraining, letting users complete setup steps in whatever order makes sense. For invited users, a welcome message on the dashboard provides orientation without over-engineering the experience. Both approaches tie directly into the empty states design, keeping the onboarding experience and the everyday UI as the same code.
