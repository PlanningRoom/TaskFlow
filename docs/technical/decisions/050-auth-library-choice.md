# Decision 050: Auth Library Choice

**Status:** Decided

**Category:** Auth Implementation

**Question:** Do we adopt an auth library/service, or build the auth flow ourselves?

**Options considered:**
- fastapi-users
- Authlib
- Managed service (Clerk, Supabase Auth, Cognito)
- Hand-rolled atop primitives

**Decision:** Hand-rolled on top of well-vetted primitives — `argon2-cffi` for hashing (Decision 048), `secrets` for token generation, FastAPI dependencies for the session middleware, SQLAlchemy for the `users` / `sessions` / `password_reset_tokens` / `invitations` tables.

**Rationale:** The auth surface is small and well-defined: email/password sign-up, login, logout, password reset, invitation accept. `fastapi-users` and similar libraries abstract social login, MFA, and flexible backends we explicitly don't need (Decision 010). Managed services conflict with the no-paid-services constraint (BRD §8.2) and add a second identity system. Hand-rolling gives full control over the session and CSRF plumbing (Decisions 047 and 051).
