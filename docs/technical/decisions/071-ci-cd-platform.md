# Decision 071: CI/CD Platform

**Status:** Decided

**Category:** Ops & Observability

**Question:** Where do CI and CD run?

**Options considered:**
- GitHub Actions
- GitLab CI
- AWS CodePipeline + CodeBuild
- CircleCI

**Decision:** GitHub Actions.

Two workflows:
- `.github/workflows/ci.yml` — runs on every PR. Jobs: type-check (frontend + backend), lint (Biome + Ruff), unit tests (Vitest + pytest), integration tests (pytest against ephemeral Postgres), Playwright smoke (Decision 080), axe accessibility checks (Decision 081), Dependabot alerts review.
- `.github/workflows/deploy.yml` — runs on push to `main`, gated on the `production` environment's manual approval (Decision 073). Builds `linux/arm64` Docker images (the only target arch — Decision 038), pushes to ECR, deploys the CloudFormation stack (Decision 087), runs Alembic migrations, rolls the Docker Compose service on EC2 via SSM Run Command.

**Rationale:** User constraint. GitHub Actions is free for public repos, well-integrated with the code host, and has a mature marketplace for AWS-specific steps (credentials via OIDC to an IAM role, ECR login, CloudFormation deploy).
