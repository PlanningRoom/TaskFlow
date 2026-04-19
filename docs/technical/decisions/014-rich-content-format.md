# Decision 014: Rich Content Format

**Status:** Decided

**Category:** Content Model

**Question:** What format do task descriptions and comments use?

**Decision:** Markdown. Task descriptions and comments are authored and stored as Markdown, rendered client-side. Supports bold, italic, lists, links, code blocks, and headers.

**Rationale:** Inherited from PRD §6.1, §11.1 and Product Decision 009. Markdown is ubiquitous, keeps storage simple (plain text), avoids WYSIWYG complexity, and is easy to diff. Rendering library and XSS sanitization policy are decided in Decision 060.
