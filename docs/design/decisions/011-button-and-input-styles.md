# Decision 011: Button & Form Input Styles

**Status:** Decided

**Category:** Component & Interaction Patterns

**Question:** What is the visual style for buttons (rounded vs squared corners, filled vs outlined variants, sizing) and form inputs (border style, focus treatment, label placement)?

**Decision:** Moderately rounded corners (6–8px border radius) for buttons, inputs, cards, and panels. Button variants:

- **Primary:** Filled with indigo background, white text. Used for main actions (Create Project, Create Task, Save).
- **Secondary:** Outlined with indigo border and text, transparent background. Used for supporting actions.
- **Ghost:** No border, subtle hover background. Used for toolbar actions, icon buttons.
- **Destructive:** Filled red for irreversible actions (Remove User, Delete Account).

Form inputs use a 1px border in medium gray, with an indigo focus ring (2px). Labels are positioned above inputs. Inputs have the same border radius as buttons for visual consistency.

**Rationale:** The 6–8px radius hits the sweet spot for minimal & soft modern — rounded enough to feel friendly, not so rounded that it looks bubbly. Four button variants cover all interaction needs without proliferating styles. The consistent border radius across buttons, inputs, and cards creates visual cohesion. Above-label input placement is the most accessible pattern and works well across form widths.
