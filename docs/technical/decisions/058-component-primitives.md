# Decision 058: Component Primitives Library

**Status:** Decided

**Category:** Client Architecture

**Question:** Which headless primitives back accessible components?

**Options considered:**
- Radix UI
- Headless UI
- Ark UI (Zag.js)
- shadcn/ui (styled Radix, copy-paste)
- Build from scratch

**Decision:** Radix UI primitives, styled with Tailwind (shadcn/ui-style — components copied into `apps/web/src/components/ui/` rather than installed as a component library).

Radix primitives used: Dialog (modals, task detail panel), DropdownMenu (user menu, sort, filter), Popover, Tooltip, Select (status, priority, assignee), Toast, Tabs (settings), Checkbox, RadioGroup, Toggle.

**Rationale:** Accessibility is a hard requirement (Decision 017). Radix's focus trapping, roving tab index, and screen-reader semantics are audited, battle-tested, and keep us on the WCAG AA line. The shadcn/ui "own your components" pattern avoids the lock-in of a styled component library while getting Radix's a11y guarantees for free.
