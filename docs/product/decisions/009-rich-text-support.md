# Decision 009: Rich Text Support

**Status:** Decided

**Category:** Task Features

**Question:** Do task descriptions and comments support formatted text (Markdown, rich text editor with bold/italic/lists/links), or are they plain text only?

**Decision:** Task descriptions and comments support Markdown formatting. Users write in Markdown and the rendered output displays formatted text (bold, italic, lists, links, code blocks, etc.).

**Rationale:** Markdown is a good middle ground — it's widely familiar, lightweight to implement (many rendering libraries exist), and doesn't require a complex rich text editor component. It allows users to structure descriptions and comments meaningfully (lists, headers, code snippets) without the overhead of a WYSIWYG editor. A rich text editor can be layered on top of Markdown storage later if needed.
