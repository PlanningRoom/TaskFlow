# Decision 036: Hosting Platform

**Status:** Decided

**Category:** Stack Foundations

**Question:** Where does TaskFlow run in production?

**Options considered:**
- AWS EC2 (various sizes)
- PaaS (Fly.io, Railway, Render)
- Managed container (AWS Fargate, Cloud Run)
- Vercel/Netlify + managed Postgres

**Decision:** A single AWS EC2 `t4g.small` instance (ARM64, 2 vCPU, 2 GB RAM) in us-east-1 (Decision 037). The instance runs Docker Compose with three containers: the FastAPI app (Uvicorn), PostgreSQL 16, and nginx (reverse proxy + origin TLS termination + static asset serving). **Cloudflare** provides DNS and proxies the zone (edge TLS + CDN/DDoS, Decision 085); an S3 bucket stores backups; **Resend** sends email (Decision 067).

> **Amendment (2026-06-14):** DNS moved from **Route 53** to **Cloudflare** (proxied), and email from **Amazon SES** to **Resend** (Decision 067). DNS and email-auth records (SPF/DKIM/DMARC) are managed in Cloudflare, outside CloudFormation — see Decision 087.

**Rationale:** User constraint. Consolidating Postgres, app, and nginx on one host keeps costs near zero — no ALB, no RDS, no ECS control-plane overhead. `t4g.small` ARM instances are the cheapest tier with enough RAM (2 GB) to run everything at demo scale. Trade-offs: vertical-only scaling; Postgres shares memory with the app; no automatic failover — acceptable for a demonstration project.
