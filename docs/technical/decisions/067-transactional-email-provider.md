# Decision 067: Transactional Email Provider

**Status:** Decided

**Category:** Supporting Services

**Question:** Which service delivers invitation and password-reset emails?

**Options considered:**
- Amazon SES
- Resend
- Postmark
- SendGrid / Mailgun

**Decision:** Amazon SES.

- Same AWS account and region as the app (Decision 037).
- Send is free from EC2 within the 62,000-emails/month SES free tier.
- Python integration: `aioboto3` `client("ses").send_email` (async to match the rest of the asyncio stack).
- From address: a verified subdomain (e.g., `noreply@taskflow.{domain}`) with SPF, DKIM, and DMARC records in Route 53.
- Local dev uses MailHog instead (Decision 039). Transport is selected via the `EMAIL_BACKEND` environment variable (`smtp` → MailHog/aiosmtplib, `ses` → Amazon SES); default is `smtp`. In production the value is hydrated from AWS SSM Parameter Store per Decision 073.

Two email templates: invitation, password reset. Minimal HTML + plaintext alternative.

**Rationale:** SES is the AWS-native choice — no third-party account, no extra secrets, lowest operational surface. Running from EC2 qualifies for the generous free tier. Bounce/complaint handling via SNS → CloudWatch alarm can be added later; at launch we simply log bounce notifications.
