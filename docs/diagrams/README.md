# Infrastructure Diagrams

Architecture diagrams for TaskFlow's production stack. Each diagram is hand-authored
as SVG (the source of truth) and rendered to a 2× PNG for embedding in docs/slides.

| # | Diagram | Shows | Grounded in |
|---|---------|-------|-------------|
| 01 | [Production network & request path](01-prod-network-request-path.svg) | End-user → Cloudflare edge → Elastic IP → EC2 (nginx → web/api → Postgres), plus AWS-managed services and Resend | TDD §5 |
| 02 | [Container composition](02-container-composition.svg) | The four `docker-compose.prod.yml` containers, ports, volumes, host mounts, and in-process jobs | TDD §5.2–§5.3 |
| 03 | [CloudFormation stack map](03-cloudformation-stack-map.svg) | The seven Part I2 stacks, their key resources, and cross-stack references | TDD §5.1 · ADR 087 |
| 04 | [CI/CD pipeline](04-cicd-pipeline.svg) | `deploy.yml` on push to `main`: OIDC → build → ECR → CFN deploy → SSM migrate/restart → health smoke | TDD §14.2 · Part I3 |

## Regenerating the PNGs

The renderer drives the chromium that Playwright already installs for the
`@taskflow/e2e` package — no Graphviz or extra dependency needed.

```sh
node docs/diagrams/render.mjs        # 2× PNGs (default)
node docs/diagrams/render.mjs 3      # 3× for print/slides
```

It converts every `*.svg` in this folder to a same-named `*.png` at the SVG's
exact dimensions. Edit the SVG, re-run, commit both files.

## Conventions

- **Solid border** = a thing that runs (container, AWS resource, CFN stack).
- **Dashed border** = a boundary (AWS account, VPC) or something external (Cloudflare/Resend).
- **Amber** = AWS / CloudFormation · **orange** = Cloudflare · **green** = nginx/host ·
  **blue** = api/network · **purple** = web/iam · **postgres-blue** = db.
- DNS, edge TLS, and email auth are **not** in CloudFormation — they live in
  Cloudflare and Resend (ADR 036 / 067 / 085).
