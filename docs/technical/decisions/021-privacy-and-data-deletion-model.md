# Decision 021: Privacy & Data Deletion Model

**Status:** Decided

**Category:** Cross-Cutting Concerns

**Question:** How does TaskFlow handle user account deletion and personal data?

**Decision:** GDPR-aware practices: collect minimal personal data; users may delete their account; on deletion, personal data (name, email, password) is removed while workspace content (tasks, comments) is retained and anonymized; assignments are cleared. No formal compliance certifications targeted.

**Rationale:** Inherited from BRD §7.5, PRD §20.2, and Business Decision 024. Anonymization (rather than content removal) preserves workspace continuity — the chosen implementation pattern is decided in Decision 065.
