# Decision 005: Responsive Web Strategy

**Status:** Decided

**Category:** Platform & Topology

**Question:** Do we ship separate layouts per device class, or a single responsive codebase?

**Decision:** A single responsive codebase serves desktop, tablet, and mobile browsers, with breakpoints at 768px and 1024px as defined in DRD §6.2.

**Rationale:** Inherited from BRD PA-02 and Design Decisions defining responsive breakpoints. One codebase keeps maintenance low. The board view degrades gracefully on mobile (columns stack; drag-and-drop replaced by status dropdown per PRD §8.4).
