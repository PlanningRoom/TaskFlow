# Decision 016: Time & Time Zone Handling

**Status:** Decided

**Category:** Content Model

**Question:** How are timestamps stored and presented?

**Decision:** Timestamps are stored in UTC (ISO 8601). The client renders them in the user's local time zone using the browser's `Intl` API. Due dates represent end-of-day in the user's local time zone (PRD §6.4).

**Rationale:** Inherited from BRD IL-05 and Business Decision 030. UTC storage is the canonical pattern for distributed systems — it avoids ambiguity at DST transitions and supports future multi-region work cheaply. Locale display is a client concern only.
