# Decision 056: Form Handling Library

**Status:** Decided

**Category:** Client Architecture

**Question:** How are forms built?

**Options considered:**
- React Hook Form + Zod
- Formik + Yup
- TanStack Form
- Hand-rolled

**Decision:** React Hook Form + Zod via `@hookform/resolvers/zod`.

- Zod schemas live in `apps/web/src/forms/schemas/` and define client-side validation.
- Each Zod schema mirrors a Pydantic model on the backend (Decision 042). They are kept in sync manually; drift is caught by integration tests and by the generated TypeScript types for API shapes.
- Inline field errors display on blur and on submit, per PRD §18.1.
- Role-aware disabling: viewer-mode forms render as read-only rather than as hidden — preserves the role-aware empty-state pattern (PRD §3.5).

**Rationale:** React Hook Form has the best performance and smallest re-render footprint in the React forms ecosystem; Zod pairs with it via a well-maintained resolver. Shared schema source between frontend forms and a (separate) backend Pydantic definition is the unavoidable cost of the cross-language stack (Decision 028).
