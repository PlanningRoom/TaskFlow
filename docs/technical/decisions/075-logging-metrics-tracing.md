# Decision 075: Logging, Metrics & Tracing

**Status:** Decided

**Category:** Ops & Observability

**Question:** What captures application logs, metrics, and traces?

**Options considered:**
- Structured stdout + hosting-platform logs
- Managed third-party (Datadog, Honeycomb, Grafana Cloud)
- Self-hosted Grafana + Loki + Prometheus
- CloudWatch (AWS-native)

**Decision:** AWS CloudWatch — no third-party services.

**Logs:**
- FastAPI configures `structlog` for JSON output to stdout.
- Docker's `awslogs` log driver ships container stdout/stderr to a CloudWatch Logs group `/taskflow/prod/api`, `/taskflow/prod/web`, `/taskflow/prod/db`.
- Log retention: 30 days.
- Every request log includes: `request_id`, `user_id` (if authenticated), `workspace_id`, `path`, `method`, `status`, `duration_ms`.
- PII (email, names) never logged.

**Metrics:**
- CloudWatch Agent on EC2 reports `mem_used_percent`, `disk_used_percent`, `cpu_usage_active`, `cpu_usage_iowait`. Alarms defined in Decision 077.
- Application-level metrics (request counts by status, WebSocket connection count) emitted as CloudWatch Logs metric filters — no push required, queryable via Logs Insights.

**Tracing:** Not implemented at launch. OpenTelemetry SDK (Python + OTEL JS) can be added later pointing at CloudWatch X-Ray if we need it.

**Rationale:** User constraint — no third-party observability. CloudWatch is the AWS-native fit. Logs Insights covers most debugging use cases; metric filters let us alert on error rates without a separate metrics pipeline.
