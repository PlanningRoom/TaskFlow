# Decision 032: Backend Framework

**Status:** Decided

**Category:** Stack Foundations

**Question:** Which framework structures the backend?

**Options considered:**
- FastAPI
- Django / Django REST Framework
- Flask
- Starlette (FastAPI's underlying toolkit)

**Decision:** FastAPI 0.110+ running on Uvicorn (ASGI).

**Rationale:** User constraint. FastAPI pairs with Pydantic (Decision 042) for validated request/response models, auto-generates the OpenAPI schema that drives frontend type generation, supports async I/O for real-time workloads, and has first-class WebSocket support for Decision 044. Its minimal-by-default design fits the t4g.small memory footprint better than Django.
