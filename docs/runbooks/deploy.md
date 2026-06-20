# TaskFlow Deployment Runbook

Operator guide for standing up and operating the TaskFlow production stack. The
infrastructure is authored as CloudFormation in `infra/cloudformation/` (Phase
I2); the CD pipeline that automates image build + stack deploy + service roll is
Phase I3 (`.github/workflows/deploy.yml`), and the first live cutover is Phase
I4. This runbook is the manual fallback and the source of the out-of-band steps
CloudFormation cannot perform.

Architecture: a single `t4g.small` (arm64) EC2 host runs four containers
(`nginx`, `api`, `web`, `db`) via `docker-compose.prod.yml`, behind the
Cloudflare proxy. See TDD §5 / §13 / §14, and the diagrams in
[`docs/diagrams/`](../diagrams/README.md): [production network & request
path](../diagrams/01-prod-network-request-path.svg), [container
composition](../diagrams/02-container-composition.svg), and the [CloudFormation
stack map](../diagrams/03-cloudformation-stack-map.svg) of the seven stacks this
runbook deploys.

---

## 0. Prerequisites (one-time, per AWS account)

- AWS CLI v2 configured with admin access for the **first** bootstrap (later
  deploys use the OIDC `taskflow-deploy-role`, no long-lived keys).
- A Cloudflare account with the zone for your domain.
- A Resend account.
- Region: default `us-east-1` (override per-stack with `--region`).

---

## 1. Deploy the CloudFormation stacks (in order)

Cross-stack `Export`/`ImportValue` wiring requires this order:

```
network -> iam -> container-registry -> storage -> parameters -> monitoring -> compute
```

```bash
REGION=us-east-1
deploy () { # deploy <stack-suffix> <template> [params...]
  aws cloudformation deploy \
    --region "$REGION" \
    --stack-name "taskflow-$1" \
    --template-file "infra/cloudformation/$2" \
    --capabilities CAPABILITY_NAMED_IAM \
    "${@:3}"
}

deploy network            network.yml
deploy iam                iam.yml \
  --parameter-overrides GitHubOrg=PlanningRoom GitHubRepo=TaskFlow
deploy container-registry container-registry.yml
deploy storage            storage.yml
deploy parameters         parameters.yml
deploy monitoring         monitoring.yml \
  --parameter-overrides AlertEmail=ops@example.com   # or set in I5
deploy compute            compute.yml
```

Grab the outputs you'll need:

```bash
aws cloudformation describe-stacks --region "$REGION" --stack-name taskflow-compute \
  --query "Stacks[0].Outputs" --output table     # Elastic IP (PublicIp), InstanceId
aws cloudformation describe-stacks --region "$REGION" --stack-name taskflow-iam \
  --query "Stacks[0].Outputs" --output table     # DeployRoleArn (-> GitHub secret)
```

> **Note — SecureString limitation.** CloudFormation cannot create SecureString
> SSM parameters. The `parameters` stack creates only the KMS key
> (`alias/taskflow-prod`) and grants the instance role decrypt. The secret
> *values* are created out-of-band in step 2.

---

## 2. Populate runtime secrets in SSM (out-of-band)

Create each parameter as a SecureString under the stack's CMK. The five from
ADR 073 plus `postgres_password` (the db container's password; it must match the
password embedded in `database_url`):

```bash
put () { aws ssm put-parameter --region "$REGION" --overwrite \
  --type SecureString --key-id alias/taskflow-prod --name "$1" --value "$2"; }

PG_PW='<generate-a-strong-password>'
put /taskflow/prod/postgres_password   "$PG_PW"
put /taskflow/prod/database_url        "postgresql+asyncpg://taskflow:${PG_PW}@db:5432/taskflow"
put /taskflow/prod/session_secret      "$(openssl rand -base64 48)"
put /taskflow/prod/csrf_secret         "$(openssl rand -base64 48)"
put /taskflow/prod/resend_api_key      're_xxxxxxxx'            # from Resend (step 4)
put /taskflow/prod/email_from_address  'no-reply@taskflow.example.com'
```

The EC2 bootstrap (`infra/ec2/user-data.sh`) reads `/taskflow/prod/*` at boot,
upper-cases the leaf names, and writes `/opt/taskflow/.env`.

---

## 3. Cloudflare (DNS + origin TLS) — ADR 036 / 085

1. **Origin CA cert.** Cloudflare dashboard → SSL/TLS → Origin Server → *Create
   Certificate*. Save the cert and key onto the host:
   - `/etc/taskflow/certs/origin.pem` (certificate)
   - `/etc/taskflow/certs/origin.key` (private key, `chmod 600`)
   (Place via SSM Session Manager / the I3 deploy step.)
2. **Encryption mode.** SSL/TLS → Overview → **Full (strict)**.
3. **DNS.** DNS → add a **proxied** (orange-cloud) `A` record:
   `taskflow` → the Elastic IP from the `compute` stack output. TTL Auto.
4. **HSTS** is emitted by nginx already (ADR 083); optionally also enable at the
   edge.

---

## 4. Resend (transactional email) — ADR 067

1. Resend dashboard → add your sending domain → it generates SPF, DKIM, and a
   DMARC suggestion.
2. Add those records to **Cloudflare DNS** (DNS-only / grey-cloud as Resend
   directs). Wait for Resend to mark the domain *Verified*.
3. Create an API key; store it in SSM as `/taskflow/prod/resend_api_key`
   (step 2).

---

## 5. First deploy of the application (Phase I4)

Until the I3 pipeline exists, ship the runtime artifacts to the host and roll the
stack manually (via SSM Session Manager or the deploy role):

```bash
# On the host (/opt/taskflow):
#   - docker-compose.prod.yml
#   - infra/nginx/nginx.conf  (referenced by the compose bind-mount path)
#   - /etc/taskflow/certs/origin.{pem,key}
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY"
docker compose -f /opt/taskflow/docker-compose.prod.yml pull
docker compose -f /opt/taskflow/docker-compose.prod.yml up -d --remove-orphans

# DB migrations (also run by the I3 pipeline):
docker compose -f /opt/taskflow/docker-compose.prod.yml run --rm api alembic upgrade head
```

Smoke check:

```bash
curl -fsS https://taskflow.example.com/health        # {"status":"ok"}
```

Manual acceptance (I4 DoD): signup → create project → create task → invite →
real-time update. Then verify SSL Labs ≥ A and Mozilla Observatory ≥ A.

---

## 6. CI/CD identity

Set the GitHub repo/environment secret `AWS_DEPLOY_ROLE_ARN` to the `taskflow-iam`
output `DeployRoleArn`. The deploy workflow (I3) assumes it via OIDC — no AWS
keys are stored anywhere (TDD §14.3).

---

## 7. Rollback (TDD §14.4)

- **App image:** redeploy the prior tag — `IMAGE_TAG=<prior-sha> docker compose
  -f /opt/taskflow/docker-compose.prod.yml up -d`. The previous image is still in
  ECR (lifecycle keeps the last 10).
- **Schema:** roll forward with a corrective migration; do not run `downgrade` in
  prod.
- **Infrastructure:** `aws cloudformation cancel-update-stack --stack-name
  taskflow-<stack>` reverts an in-progress update; otherwise redeploy the prior
  template revision.

---

## 8. Monitoring (Phase I5)

- Confirm the operator email subscription to the `taskflow-alerts` SNS topic
  (set `AlertEmail` on the `monitoring` stack, then confirm via the email link).
- Synthesize each alarm and confirm an email arrives (status check, error_count,
  5xx_count, mem/disk, login_failure).
- Verify each metric filter matches live log lines in CloudWatch Logs Insights
  (the filters key off lowercase `level`, numeric `status`, and the `event` key —
  see `infra/cloudformation/monitoring.yml`).
