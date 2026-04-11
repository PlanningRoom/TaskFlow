# Decision 014: Animation & Motion Scope

**Status:** Decided

**Category:** Component & Interaction Patterns

**Question:** What level of animation should TaskFlow invest in — none, subtle (panel transitions, fade-ins), or rich (drag feedback, micro-interactions, notification toasts)? This is a scope decision that affects design and implementation effort.

**Decision:** Subtle animations only. Specifically:

- **Panel transitions:** Side panel slides in/out (200–250ms ease-out). Modals fade in with slight scale (150ms).
- **Hover states:** Background color transitions on buttons, cards, and list rows (150ms).
- **Drag-and-drop:** Drop target column highlights during drag. Placeholder shows where the card will land.
- **Notification badge:** Gentle pulse or scale animation when a new notification arrives.
- **No:** Page transition animations, loading spinners with elaborate motion, parallax, or decorative animations.

All animations respect `prefers-reduced-motion` — users with this OS setting see instant state changes with no transitions.

**Rationale:** Subtle animation reinforces the soft modern personality by making the UI feel responsive and polished without being distracting. The minimal personality aspect keeps it restrained — motion serves function (spatial orientation, feedback), not decoration. Respecting `prefers-reduced-motion` is required for WCAG 2.1 AA compliance and costs almost nothing to implement.
