# Decision 029: Right-to-Left Language Support

**Status:** Decided

**Category:** Accessibility & Localization

**Question:** Does TaskFlow need to support right-to-left (RTL) languages such as Arabic or Hebrew?

**Decision:** No RTL support at launch, but use CSS logical properties throughout. Using `margin-inline-start` instead of `margin-left`, etc., makes the codebase RTL-ready so that adding RTL language support later is largely automatic.

**Rationale:** English is the only language at launch, so RTL has no immediate users. CSS logical properties are the modern standard, well-supported in all current browsers, and require negligible extra effort versus physical properties. This mirrors the i18n approach from Decision 028 — architect for the future without building for it today.
