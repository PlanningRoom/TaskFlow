# Decision 012: Overlay & Panel Patterns

**Status:** Decided

**Category:** Component & Interaction Patterns

**Question:** The PRD specifies a side panel for task detail. What pattern should other interactions use — settings, invitations, label management, delete confirmations? Options include modals, side panels, inline expansion, and full-page views. Which pattern applies where?

**Decision:** Three patterns, each used for a specific type of interaction:

- **Side panel (overlay):** Task detail view. Slides in from the right, overlays the current view with a dimmed backdrop. This is the primary pattern for viewing and editing task content without losing context of the board/list.
- **Modal dialog:** Destructive confirmations (Remove User, Delete Account), invitation form, label create/edit. Used for focused, short interactions that require a decision before continuing.
- **Inline / page-level:** Settings pages (workspace settings, profile settings, member management). These are full sections within the settings area, not overlays, since they involve browsing and editing multiple items.

**Rationale:** Matching the overlay pattern to the interaction type keeps the experience predictable. Side panels preserve context (the user can still see the board behind it), making them ideal for task detail where users frequently open and close tasks while scanning the board. Modals force focus for decisions that shouldn't be accidental (destructive actions) or that are quick and self-contained (invite a user). Settings get their own pages because they involve lists, tables, and multiple edits — cramming them into a modal or panel would feel constrained.
