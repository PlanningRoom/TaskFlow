# Decision 019: Notification Preferences

**Status:** Decided

**Category:** Notifications

**Question:** Can users control which notifications they receive (e.g., mute a project, disable status change alerts), or is the notification set fixed for all users?

**Decision:** The notification set is fixed for all users at launch. No user-configurable notification preferences.

**Rationale:** The notification trigger set (Decision 018) is already focused on high-signal events — assignments, mentions, status changes, and comments on your tasks. With a curated set of triggers, the risk of notification fatigue is low for teams of 10–50 users. Adding preferences introduces settings UI, per-user configuration storage, and conditional notification logic — significant complexity for a feature that solves a problem users may not have. Preferences can be added in a future iteration if users find the fixed set too noisy.
