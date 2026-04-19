# Decision 060: Markdown Rendering & Sanitization

**Status:** Decided

**Category:** Client Architecture

**Question:** How is user-authored Markdown rendered safely?

**Options considered:**
- `react-markdown` + `remark-gfm` + `rehype-sanitize`
- `markdown-it` + DOMPurify
- `marked` + DOMPurify
- Server-side render to HTML, serve sanitized

**Decision:** `react-markdown` with a `remark-gfm` + `rehype-sanitize` pipeline. Rendering happens on the client at display time — Markdown stored raw in the database.

- **Allowed Markdown:** bold, italic, strikethrough, inline code, fenced code blocks, headers H1–H6, ordered/unordered lists, blockquotes, tables, links.
- **Disallowed:** raw HTML (no pass-through), images (file attachments are out of scope — Decision 015; link to external hosts in Markdown is fine, inline `<img>` is not), footnotes.
- **Links:** external links rendered with `target="_blank" rel="noopener noreferrer nofollow"`. `javascript:` and `data:` URIs stripped by `rehype-sanitize`.
- **@mentions:** a custom remark plugin runs before sanitize — detects `@username` tokens against the workspace member list and transforms them into styled `<span class="mention">` elements (not anchor tags). @mentions outside the member list remain plain text.

**Rationale:** The unified/remark/rehype pipeline is the React standard for Markdown. `rehype-sanitize` is strict allowlist by default. Rendering on the client keeps the backend simpler and means no stored-HTML XSS surface. Strict CSP (Decision 083) is the backstop if sanitization ever fails.
