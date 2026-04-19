# Decision 042: Request/Response Validation

**Status:** Decided

**Category:** API & Real-Time

**Question:** How are API inputs validated and outputs shaped?

**Options considered:**
- Pydantic v2 (FastAPI-native)
- marshmallow
- Hand-written validators

**Decision:** Pydantic v2 for backend. Every FastAPI endpoint declares request and response models as Pydantic classes. Pydantic powers FastAPI's OpenAPI schema generation.

Frontend TypeScript types for the API are generated from the OpenAPI schema via `openapi-typescript`, run as part of the frontend build. Frontend form validation (Decision 056) uses Zod schemas that mirror the Pydantic definitions — kept in sync manually.

**Rationale:** Pydantic is the FastAPI default — no friction. OpenAPI-to-TypeScript generation gives the frontend compile-time assurance that it is calling the API with the right shapes, without duplicating model definitions by hand. Zod vs. Pydantic duplication is the residual cost of a cross-language stack (Decision 028); it is small and caught by integration tests.
