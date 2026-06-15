# Decision 067: Transactional Email Provider

**Status:** Decided

**Category:** Supporting Services

**Question:** Which service delivers invitation and password-reset emails?

**Options considered:**
- Amazon SES
- Resend
- Postmark
- SendGrid / Mailgun

**Decision:** Resend.

- Python integration: the Resend HTTP API called via `httpx` (async, to match the asyncio stack). No AWS SDK.
- From address: a verified subdomain (e.g., `noreply@taskflow.{domain}`). Resend's required SPF, DKIM, and DMARC records are added in **Cloudflare DNS** (Decision 036), not Route 53.
- Local dev uses MailHog instead (Decision 039). Transport is selected via the `EMAIL_BACKEND` environment variable (`smtp` → MailHog/aiosmtplib, `resend` → Resend HTTP API); default is `smtp`. In production the value (and the `RESEND_API_KEY`) is hydrated from AWS SSM Parameter Store per Decision 073.

Two email templates: invitation, password reset. Minimal HTML + plaintext alternative.

**Rationale:** Resend has a first-class developer experience, a simple HTTP API (no AWS SES sandbox/production-access approval step, no IAM-for-SES policy surface), and good deliverability + bounce/complaint visibility in its dashboard/webhooks. It is the one deliberate non-AWS dependency in the stack (TDD §5 principle 4), traded for DX and faster setup. The cost is one third-party account + one secret (`RESEND_API_KEY`).

---

**Amendment (2026-06-14):** switched from **Amazon SES** to **Resend**, made alongside the move from Route 53 to Cloudflare DNS (Decision 036). Original SES rationale: AWS-native, free-tier send from EC2, lowest cross-vendor surface — superseded by the DX/setup benefits above. **Code impact:** the D2 email adapter shipped with an SES (`aioboto3`) implementation; the prod adapter is swapped to a Resend HTTP-API implementation as part of **Phase I2** (the dev SMTP→MailHog path is unchanged). See the implementation-status note dated 2026-06-14.
