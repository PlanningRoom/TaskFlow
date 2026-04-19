# Decision 077: Uptime Monitoring

**Status:** Decided

**Category:** Ops & Observability

**Question:** How do we detect that TaskFlow is down?

**Options considered:**
- Free third-party (UptimeRobot, Better Stack)
- CloudWatch Synthetics canary
- CloudWatch alarms on EC2 and application metrics
- Self-hosted Uptime Kuma

**Decision:** CloudWatch alarms, no third-party service.

Alarms (all routed to an SNS topic `taskflow-alerts` subscribed to the operator's email):

| Alarm | Source | Condition |
|---|---|---|
| Instance down | EC2 `StatusCheckFailed` | ≥ 1 for 2 consecutive minutes |
| High error rate | Logs metric filter on 5xx | ≥ 10 5xx responses / 5 min |
| Unhandled exception spike | Logs metric filter on ERROR level (Decision 076) | ≥ 5 ERRORs / 5 min |
| Disk pressure | `disk_used_percent` | ≥ 80% for 10 min |
| Memory pressure | `mem_used_percent` | ≥ 85% for 10 min |

Also: the FastAPI app exposes `GET /health` that checks DB connectivity. A CloudWatch Synthetics canary (optional, if cost remains acceptable) pings it every 5 minutes.

**Rationale:** User constraint — no third-party. CloudWatch alarms cover both infrastructure health and application-level failure. SNS-to-email is the simplest delivery. For a single operator running a demo project, this is sufficient.
