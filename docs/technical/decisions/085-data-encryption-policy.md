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
- **Public TLS terminates at the Cloudflare edge** (the zone is proxied — "orange cloud" — per Decision 036). The **edge↔origin** hop is secured by a long-lived **Cloudflare Origin CA certificate** installed on the EC2 host and served by nginx; Cloudflare is set to **Full (strict)** so it validates that origin cert. No Let's Encrypt / `certbot` and no renewal cron — the Origin CA cert is valid for years and Cloudflare manages the public-facing edge cert.
- HSTS with preload (Decision 083) — emitted at the edge and/or origin.
- WebSockets over `wss://` only (Cloudflare proxies WebSockets).

**At rest:**
- EC2 EBS volumes encrypted with the default AWS-managed KMS key (enabled by default on new AWS accounts; enforced via the CloudFormation template per Decision 087).
- S3 backup bucket encrypted with SSE-S3.
- Passwords stored as Argon2id hashes (Decision 048), never plaintext.

**No application-level column encryption.** TaskFlow collects only email, display name, and hashed passwords as personal data (Decision 021). No payment data, no health data, no national identifiers.

**Rationale:** Standard baseline encryption posture. Column-level encryption introduces key management complexity without a corresponding benefit given the thin personal-data surface.

---

**Amendment (2026-06-14):** in-transit TLS moved from **Let's Encrypt + certbot on the origin** to **Cloudflare edge TLS + a Cloudflare Origin CA certificate** (made with the Route 53 → Cloudflare DNS switch, Decision 036). This removes the certbot container, the renewal cron, and the ACM cert, and adds Cloudflare's CDN/DDoS protection in front of the origin. TLS 1.3 and HSTS preload are unchanged. **Code/infra impact:** the nginx cert paths and `docker-compose.prod.yml` (no `certbot` service) change in **Phase I2**; the E1 `nginx.conf` currently references Let's Encrypt paths and is updated then.
