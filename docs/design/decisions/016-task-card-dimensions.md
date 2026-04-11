# Decision 016: Task Card Size & Shape

**Status:** Decided

**Category:** Board & Task Design

**Question:** How large should task cards be on the board? Compact single-line cards showing minimal info, or taller multi-line cards with more metadata visible? What is the balance between information density and scannability?

**Decision:** Medium-height multi-line cards. Each card displays its content in a structured layout:

- **Top line:** Task title (1–2 lines, truncated with ellipsis if longer)
- **Middle row:** Label chips (up to 3 visible, "+N" overflow indicator)
- **Bottom row:** Priority icon, due date (with overdue styling), comment count icon, assignee avatar (right-aligned)

Cards have 12px internal padding, the same 6–8px border radius as other components, a subtle border or shadow to separate them from the column background, and a hover state (slight elevation or border change). Estimated height: ~100–120px depending on content.

**Rationale:** Medium cards balance scannability with information density. Showing the key metadata (priority, due date, labels, assignee) on the card lets users assess tasks without opening the detail panel, which is important for board-based workflows. The structured layout with consistent zones (title top, metadata bottom) makes cards scannable even in long columns. This matches the PRD's task card specification while keeping the overall feel clean.
