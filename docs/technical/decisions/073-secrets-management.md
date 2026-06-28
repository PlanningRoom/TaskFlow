# Decision 073: Secrets Management

**Status:** Decided

**Category:** Ops & Observability

**Question:** Where are secrets stored and delivered to the application?

**Options considered:**
- GitHub Secrets (CI-only)
- AWS Secrets Manager
- AWS Systems Manager Parameter Store
- Self-hosted (Vault)

**Decision:** Split by concern — CI-level secrets in GitHub, runtime secrets in AWS Parameter Store.

**CI-level secrets** (used by GitHub Actions workflows): stored as GitHub repository and environment secrets, scoped to a GitHub `production` environment that requires manual approval for deploys. The `deploy.yml` job declares `environment: production` so a push to `main` pauses for the required-reviewer approval before any step runs.
- `AWS_DEPLOY_ROLE_ARN` — an IAM role assumed via OIDC federation (no long-lived AWS keys). This is the **only** stored CI secret.

> **Amendment (2026-06-28, Phase I3):** the ECR **registry URL is not stored as a secret**. It is derived at deploy time from the `aws-actions/amazon-ecr-login` step's `registry` output (`<account>.dkr.ecr.<region>.amazonaws.com` — an identifier, not a secret), which avoids a redundant value that could drift from the account. The earlier `ECR_REPOSITORY` secret is dropped.

**Runtime secrets** (used by the FastAPI app on EC2): stored in AWS Systems Manager Parameter Store as `SecureString` parameters under `/taskflow/prod/`:
- `/taskflow/prod/database_url`
- `/taskflow/prod/session_secret`
- `/taskflow/prod/csrf_secret`
- `/taskflow/prod/resend_api_key`
- `/taskflow/prod/email_from_address`
- Any other Resend / domain values. (Cloudflare DNS and the Cloudflare Origin CA cert are configured in Cloudflare; a Cloudflare API token only needs storing here if DNS is later automated.)

The EC2 instance has an IAM role granting read access to `/taskflow/prod/*`. The app reads these parameters at boot via `boto3.client('ssm').get_parameters_by_path(..., WithDecryption=True)` and exposes them to the process as environment variables.

**Local dev** uses a gitignored `.env.local` file loaded via `python-dotenv`; values are non-sensitive (local Postgres URL, random dev session secret).

**Rationale:** User constraint — GitHub Secrets for CI and Parameter Store (not Secrets Manager) for runtime. Parameter Store SecureString is free within quotas and adequate for a demo project; Secrets Manager adds cost and features (rotation, versioning) TaskFlow does not need. OIDC federation avoids long-lived AWS keys in GitHub Secrets.
