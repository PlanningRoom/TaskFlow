# Decision 013: Data Density & Spacing

**Status:** Decided

**Category:** Component & Interaction Patterns

**Question:** Should the UI favor compact density (more visible data, power-user feel) or comfortable density (more whitespace, approachable feel)? This affects spacing, padding, font sizes, and how much content is visible without scrolling.

**Decision:** Comfortable density with purposeful whitespace. Generous padding within cards (12–16px), clear spacing between list rows (8px gap), and breathing room around sections. The layout should feel open without being wasteful — closer to Notion than to Jira, but not as airy as a marketing site.

Specific guidelines:
- **Base spacing unit:** 4px, with common increments of 8px, 12px, 16px, 24px, 32px
- **Card padding:** 12–16px
- **List row height:** ~48px for interactive rows (comfortable click/tap target)
- **Section spacing:** 24–32px between major sections

**Rationale:** TaskFlow's audience includes both daily users and occasional viewers arriving via invitation. Comfortable density is more welcoming for new users and reduces visual overwhelm on boards with many tasks. The 48px row height meets touch target guidelines (44px minimum) for the responsive mobile layout. The 4px base unit provides a consistent rhythm that scales predictably.
