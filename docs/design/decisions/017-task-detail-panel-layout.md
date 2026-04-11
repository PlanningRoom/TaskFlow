# Decision 017: Task Detail Panel Layout

**Status:** Decided

**Category:** Board & Task Design

**Question:** How wide should the task detail side panel be — narrow (~400px) or wide (~50% of viewport)? Should it push the board content aside or overlay it? How does it behave on tablet and mobile?

**Decision:** Medium-width panel at approximately 480px, sliding in from the right as an overlay with a dimmed backdrop over the board/list. The board content remains visible but is not interactive while the panel is open. On tablet, the panel takes approximately 60% of the viewport width. On mobile, the panel opens full-screen as specified in the PRD.

The panel scrolls internally and is divided into clear sections as defined in the PRD: header (title, status, close), properties (assignee, priority, due date, labels), description, and comments.

**Rationale:** 480px provides enough width for comfortable reading and editing of task descriptions and comments (roughly 60–70 characters per line at 14px, which is optimal for readability) without completely obscuring the board. Overlaying rather than pushing the board avoids layout reflow and lets users maintain spatial awareness of where they are on the board. Full-screen on mobile is necessary because 480px would leave no usable space alongside it on small viewports.
