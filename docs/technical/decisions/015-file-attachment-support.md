# Decision 015: File Attachment Support

**Status:** Decided

**Category:** Content Model

**Question:** Can users attach files to tasks or comments?

**Decision:** No. Tasks and comments are text-only. Users may paste external links (e.g., to a shared drive) into Markdown content.

**Rationale:** Inherited from PRD §6.8 and Product Decision 008. Removes the need for object storage, upload flows, virus scanning, quota management, and preview rendering. No file-storage service is provisioned in the infrastructure.
