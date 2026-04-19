# Decision 059: Drag-and-Drop Library

**Status:** Decided

**Category:** Client Architecture

**Question:** Which library implements board-view drag-and-drop?

**Options considered:**
- `@dnd-kit/core`
- `react-dnd`
- `@hello-pangea/dnd` (ex react-beautiful-dnd)
- Native HTML5 DnD

**Decision:** `@dnd-kit/core` (no `@dnd-kit/sortable` needed — PRD §6.6 excludes intra-column reordering).

**Rationale:** `dnd-kit` has first-class keyboard accessibility — arrow keys move a "selected" draggable between drop targets, space/enter confirms — which is the keyboard-accessible alternative required by Decision 017 and PRD §16.1. Active maintenance, modern React-native API, and a modular architecture that keeps the bundle small. `hello-pangea/dnd` has a reputation for being easier but accessibility is not as strong.
