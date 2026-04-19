# Decision 085: Data Encryption Policy

**Status:** Decided

**Category:** Security Hardening

**Question:** How is data encrypted in transit and at rest?

**Options considered:**
- TLS + provider at-rest encryption
- Add column-level encryption for sensitive fields
- E2E encryption (not applicable)

**Decision:**

**In transit:**
- TLS 1.3 enforced everywhere.
- Certificate from Let's Encrypt via `certbot` running on the EC2 host, nginx serving the cert. Automated renewal via a cron job inside an nginx-adjacent container.
- HSTS with preload (Decision 083).
- WebSockets over `wss://` only.

**At rest:**
- EC2 EBS volumes encrypted with the default AWS-managed KMS key (enabled by default on new AWS accounts; enforced via the CloudFormation template per Decision 087).
- S3 backup bucket encrypted with SSE-S3.
- Passwords stored as Argon2id hashes (Decision 048), never plaintext.

**No application-level column encryption.** TaskFlow collects only email, display name, and hashed passwords as personal data (Decision 021). No payment data, no health data, no national identifiers.

**Rationale:** Standard baseline encryption posture. Column-level encryption introduces key management complexity without a corresponding benefit given the thin personal-data surface.
