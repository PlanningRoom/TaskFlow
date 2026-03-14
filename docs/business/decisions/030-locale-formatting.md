# Decision 030: Locale-Specific Formatting

**Status:** Decided

**Category:** Accessibility & Localization

**Question:** Will TaskFlow adapt formatting for locale-specific conventions such as date formats, number formats, and time zones?

**Decision:** Use the browser's locale for automatic formatting. Dates, times, and numbers will display in the user's preferred format via the JavaScript `Intl` API. Timestamps will be stored in UTC and displayed in the user's local time zone.

**Rationale:** The `Intl` API handles locale-specific formatting with minimal code and is well-supported in all modern browsers. This aligns with the i18n-ready approach from Decisions 028 and 029 — internationally appropriate formatting without building a settings UI. A user override can be added later if needed.
