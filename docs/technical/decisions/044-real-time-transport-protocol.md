# Decision 044: Real-Time Transport Protocol

**Status:** Decided

**Category:** API & Real-Time

**Question:** What protocol carries real-time updates from server to client?

**Options considered:**
- WebSockets
- Server-Sent Events
- Long polling
- HTTP/3 server push

**Decision:** WebSockets. The client connects on login to `wss://{host}/ws`; the server authenticates via the session cookie and subscribes the connection to the user's workspace and accessible projects.

**Rationale:** FastAPI has native WebSocket support that shares the same ASGI worker as HTTP endpoints — no separate service. nginx proxies WebSocket upgrade requests cleanly. Bidirectional is unnecessary today but gives headroom (e.g., typing indicators) without a protocol migration. SSE is simpler but some intermediaries still buffer long-lived HTTP responses in ways that break real-time delivery.
