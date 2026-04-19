# Decision 076: Error Tracking

**Status:** Decided

**Category:** Ops & Observability

**Question:** How are unhandled exceptions captured and reviewed?

**Options considered:**
- Sentry
- Rollbar / Bugsnag
- GlitchTip (self-hosted Sentry-compatible)
- CloudWatch Logs + metric filters

**Decision:** CloudWatch Logs, no third-party error tracker.

- A FastAPI global exception handler catches any unhandled exception, logs it at `level=ERROR` with a `exception.type`, `exception.message`, and full stack trace in the structured JSON payload (Decision 075), and returns a 500 in the Decision 043 error shape.
- Client-side: a React error boundary catches render errors and POSTs them to `/api/v1/errors/client` which logs them through the same pipeline.
- CloudWatch Logs metric filter on `{ $.level = "ERROR" }` drives an alarm (Decision 077).
- Source maps for production client bundles are uploaded to a private S3 prefix and referenced by filename when investigating.

**Rationale:** User constraint — no third-party. CloudWatch Logs is the AWS-native fit. The trade-off vs. Sentry is real: no release-over-release grouping, no breadcrumb stacks, no automatic dedup. For a demo project, Logs Insights queries are workable.
