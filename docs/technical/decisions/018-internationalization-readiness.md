# Decision 018: Internationalization Readiness

**Status:** Decided

**Category:** Cross-Cutting Concerns

**Question:** What languages does TaskFlow ship with, and how are additional languages supported architecturally?

**Decision:** Launch with English only. All user-facing strings are externalized to translation files via an i18n framework so that additional languages can be added without code changes.

**Rationale:** Inherited from BRD IL-01 / IL-02 and Business Decision 028. The architectural requirement is string externalization — no hardcoded UI text in components. The specific i18n library is selected in Decision 061.
