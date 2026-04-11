# Decision 021: Activity Feed Entry Design

**Status:** Decided

**Category:** Dashboard & Feed Design

**Question:** How should activity feed entries be formatted — sentence-style prose (e.g., "Alex moved Task X to Done"), structured rows with distinct columns for actor/action/target/time, or icon-led timeline entries?

**Decision:** Sentence-style entries with a leading avatar. Each entry follows the format:

**[Avatar] [Actor name] [action] [target] · [project name] · [relative timestamp]**

Examples:
- **[avatar] Sarah** moved **Design homepage** to **In Review** · Marketing · 2h ago
- **[avatar] Alex** commented on **Fix login bug** · Engineering · 30m ago
- **[avatar] Jordan** created **Update API docs** · Platform · 1d ago

Action verbs are bold or highlighted. Task names are clickable links. Entries are compact (single line where possible, wrapping to two if needed).

**Rationale:** Sentence-style entries are scannable and natural to read — they tell a story rather than requiring the user to parse structured columns. The avatar provides a visual anchor that helps users quickly spot activity from specific people. Relative timestamps ("2h ago") are more immediately useful than absolute times for recent activity. Keeping entries compact means more activity is visible without scrolling, which matters in the dashboard's right column where vertical space is limited.
