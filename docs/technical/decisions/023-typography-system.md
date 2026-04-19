# Decision 023: Typography System

**Status:** Decided

**Category:** Design System Foundations

**Question:** Which typeface does TaskFlow use and how is it loaded?

**Decision:** Inter, loaded via Google Fonts, with a system fallback stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`). Monospace code blocks use the system monospace stack.

**Rationale:** Inherited from DRD §3.1 and Design Decision 004. Inter is the chosen typeface from the design phase. Google Fonts is acceptable for a demonstration project; self-hosting can be revisited if privacy or performance concerns arise.
