# Decision 028: Supported Languages

**Status:** Decided

**Category:** Accessibility & Localization

**Question:** Which languages will TaskFlow support at launch?

**Decision:** English only, but architected for i18n. All user-facing strings will be externalized to translation files using an i18n framework, making it trivial to add languages later.

**Rationale:** The primary user base speaks English, so additional languages aren't needed at launch. However, retrofitting i18n into a codebase with hardcoded strings is significantly more work than setting it up from the start. Modern frontend frameworks make i18n setup lightweight.
