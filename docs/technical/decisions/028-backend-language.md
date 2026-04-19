# Decision 028: Backend Language

**Status:** Decided

**Category:** Stack Foundations

**Question:** What language powers the backend?

**Options considered:**
- Python
- TypeScript on Node.js
- Go
- Elixir
- Ruby
- Rust

**Decision:** Python 3.12+.

**Rationale:** User constraint. Python pairs with FastAPI (Decision 032) for a pragmatic, well-documented stack suited to a demonstration project. Trade-off: cross-language with the TypeScript frontend means we cannot share validation code directly — we instead generate TypeScript types from the FastAPI OpenAPI schema (Decision 042), and maintain Zod validators on the frontend separately from Pydantic models on the backend.
