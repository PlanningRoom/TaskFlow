# Decision 027: Assistive Technology Support

**Status:** Decided

**Category:** Accessibility & Localization

**Question:** Which assistive technologies must TaskFlow support (e.g., screen readers, keyboard-only navigation, voice control)?

**Decision:** Keyboard navigation and screen readers. These are the two primary assistive technologies TaskFlow will support, using semantic HTML, proper ARIA attributes, and keyboard-focusable interactive elements. Complex UI patterns like task boards will include accessible alternatives (e.g., list view).

**Rationale:** Keyboard and screen reader support are directly required to meet the WCAG 2.1 AA commitment from Decision 026. Modern component libraries provide strong defaults for both. Other assistive technologies like voice control largely work for free when these two are well-supported.
