# Decision 027: Frontend Language & Type System

**Status:** Decided

**Category:** Stack Foundations

**Question:** What language powers the frontend?

**Options considered:**
- TypeScript (strict mode)
- JavaScript
- TypeScript with JSDoc annotations only

**Decision:** TypeScript in strict mode. `tsconfig.json` has `"strict": true` from day one, enabling `strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, and related flags.

**Rationale:** The monorepo (Decision 026) depends on cross-package type sharing. The PRD's permission matrix, status and priority enums, and role-aware behavior are exactly the domain where TypeScript's discriminated unions and literal types catch bugs at compile time. Strict mode from day one avoids the painful opt-in-later migration. Types generated from the FastAPI OpenAPI schema (Decision 042) flow into the client without runtime casts.
