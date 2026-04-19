# Decision 043: Error Response Contract

**Status:** Decided

**Category:** API & Real-Time

**Question:** What is the shape of an API error response?

**Options considered:**
- RFC 7807 Problem Details
- Custom `{ error: { code, message, fields? } }`
- FastAPI defaults as-is

**Decision:** Custom JSON shape:

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "No task with that id exists in this workspace.",
    "fields": { "title": ["REQUIRED"] }
  }
}
```

- `code` — stable, machine-readable screaming snake case string. Clients branch on this.
- `message` — English fallback, suitable for logs and development. Client prefers its own translated copy keyed off `code`.
- `fields` — present only for 422 validation errors; maps field name to an array of error codes.

All HTTP error responses (400, 401, 403, 404, 409, 422, 429, 500) follow this shape. A FastAPI exception handler normalizes internal exceptions and Pydantic `ValidationError` into this envelope.

**Rationale:** RFC 7807 carries extra fields the client never needs; a small custom shape is easier to document, generate types for, and consume. Stable codes keep the contract i18n-friendly (Decision 018) — the client supplies translated copy, the server does not.
