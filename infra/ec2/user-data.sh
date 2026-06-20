#!/usr/bin/env bash
#
# TaskFlow EC2 bootstrap (TDD §5.2; ADR 073). Runs once at instance launch.
# Prepares the host (Docker, Compose plugin, CloudWatch Agent), hydrates the
# runtime secrets from SSM Parameter Store into /opt/taskflow/.env, and — once
# the deploy pipeline (I3) has shipped docker-compose.prod.yml + the Cloudflare
# Origin CA cert — brings the stack up. Self-discovers region/account from IMDS
# so it can be embedded verbatim in compute.yml (no CloudFormation substitution).
#
# Canonical copy. compute.yml embeds this file's content as instance UserData;
# keep the two in sync.
set -euo pipefail

exec > >(tee -a /var/log/taskflow-bootstrap.log) 2>&1
echo "[taskflow] bootstrap starting $(date -u +%FT%TZ)"

APP_DIR=/opt/taskflow
CERT_DIR=/etc/taskflow/certs
mkdir -p "${APP_DIR}" "${CERT_DIR}"

# ── Instance identity (IMDSv2) ───────────────────────────────────────────────
TOKEN="$(curl -sS -X PUT 'http://169.254.169.254/latest/api/token' \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 600')"
imds() { curl -sS -H "X-aws-ec2-metadata-token: ${TOKEN}" "http://169.254.169.254/latest/meta-data/$1"; }
REGION="$(imds placement/region)"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text --region "${REGION}")"
ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
echo "[taskflow] region=${REGION} account=${ACCOUNT_ID}"

# ── Docker + Compose plugin (Amazon Linux 2023, arm64) ───────────────────────
dnf install -y docker
systemctl enable --now docker
COMPOSE_PLUGIN_DIR=/usr/libexec/docker/cli-plugins
mkdir -p "${COMPOSE_PLUGIN_DIR}"
if ! docker compose version >/dev/null 2>&1; then
  curl -fsSL \
    "https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-aarch64" \
    -o "${COMPOSE_PLUGIN_DIR}/docker-compose"
  chmod +x "${COMPOSE_PLUGIN_DIR}/docker-compose"
fi

# ── CloudWatch Agent — host metrics only (container logs ship via awslogs) ────
dnf install -y amazon-cloudwatch-agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/taskflow-agent.json <<'JSON'
{
  "agent": { "metrics_collection_interval": 60 },
  "metrics": {
    "namespace": "CWAgent",
    "append_dimensions": { "InstanceId": "${aws:InstanceId}" },
    "aggregation_dimensions": [["InstanceId"]],
    "metrics_collected": {
      "mem": { "measurement": ["mem_used_percent"] },
      "disk": { "measurement": ["disk_used_percent"], "resources": ["/"] },
      "cpu": { "measurement": ["cpu_usage_active", "cpu_usage_iowait"], "totalcpu": true }
    }
  }
}
JSON
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/taskflow-agent.json

# ── Runtime secrets → /opt/taskflow/.env (ADR 073) ───────────────────────────
# SSM leaf names are lowercase; upper-case them for the conventional env vars
# the app + compose expect (settings is case-insensitive, but compose isn't).
write_env() {
  local env_file="${APP_DIR}/.env"
  : > "${env_file}"
  chmod 600 "${env_file}"
  aws ssm get-parameters-by-path \
    --path /taskflow/prod --with-decryption --region "${REGION}" \
    --query 'Parameters[*].[Name,Value]' --output text |
    while IFS=$'\t' read -r name value; do
      key="$(basename "${name}" | tr '[:lower:]' '[:upper:]')"
      echo "${key}=${value}" >> "${env_file}"
    done
  # Non-secret production settings + discovered values.
  {
    echo "APP_ENV=production"
    echo "EMAIL_BACKEND=resend"
    echo "AWS_REGION=${REGION}"
    echo "ECR_REGISTRY=${ECR_REGISTRY}"
    echo "S3_BACKUPS_BUCKET=taskflow-backups-${ACCOUNT_ID}-${REGION}"
    echo "S3_SOURCE_MAPS_BUCKET=taskflow-source-maps-${ACCOUNT_ID}-${REGION}"
  } >> "${env_file}"
  # The app's EMAIL_FROM mirrors the SSM email_from_address if present. Read the
  # value into a variable first so we never read and append the same file at once.
  local from_addr
  from_addr="$(awk -F= '/^EMAIL_FROM_ADDRESS=/{sub(/^EMAIL_FROM_ADDRESS=/, ""); print; exit}' "${env_file}")"
  if [[ -n "${from_addr}" ]]; then
    echo "EMAIL_FROM=${from_addr}" >> "${env_file}"
  fi
}
write_env

# ── ECR login ────────────────────────────────────────────────────────────────
aws ecr get-login-password --region "${REGION}" |
  docker login --username AWS --password-stdin "${ECR_REGISTRY}"

# ── Start the stack if the deploy artifacts are present ──────────────────────
# The I3 pipeline ships docker-compose.prod.yml, infra/nginx/nginx.conf, and the
# Cloudflare Origin CA cert/key (to ${CERT_DIR}) via SSM, then re-runs compose.
if [[ -f "${APP_DIR}/docker-compose.prod.yml" && -f "${CERT_DIR}/origin.pem" ]]; then
  # shellcheck source=/dev/null
  ( set -a; source "${APP_DIR}/.env"; set +a
    docker compose -f "${APP_DIR}/docker-compose.prod.yml" pull
    docker compose -f "${APP_DIR}/docker-compose.prod.yml" up -d --remove-orphans )
  echo "[taskflow] stack started"
else
  echo "[taskflow] host prepared; awaiting first deploy (compose file / cert not present yet)"
fi

echo "[taskflow] bootstrap finished $(date -u +%FT%TZ)"
