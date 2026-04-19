# Decision 020: Locale-Specific Formatting

**Status:** Decided

**Category:** Cross-Cutting Concerns

**Question:** How are dates, times, and numbers formatted for the user?

**Decision:** The client formats dates, times, and numbers using the browser's locale via the JavaScript `Intl` API (`Intl.DateTimeFormat`, `Intl.NumberFormat`, `Intl.RelativeTimeFormat`). No custom formatting libraries are added.

**Rationale:** Inherited from BRD IL-04 and Business Decision 030. The `Intl` API is built into every modern browser, handles every locale, and requires no bundle size. This keeps the dependency footprint lower and locale coverage automatic.
