from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "info"
    app_base_url: str = "http://localhost:8080"
    frontend_base_url: str = "http://localhost:5173"

    database_url: str = "postgresql+asyncpg://taskflow:taskflow@db:5432/taskflow"

    cors_allowed_origins: str = "http://localhost:5173"

    # Sessions / CSRF (ADR 047, 051; TDD §11)
    session_cookie_name: str = "taskflow_session"
    csrf_cookie_name: str = "taskflow_csrf"
    csrf_header_name: str = "X-CSRF-Token"
    session_idle_ttl_days: int = 7
    session_absolute_ttl_days: int = 30
    # None → derived from app_env (dev: insecure so cookies persist over http://localhost;
    # prod: Secure). Set COOKIE_SECURE explicitly to override the derived default.
    cookie_secure: bool | None = None

    # Real-time fan-out (ADR 044, 045; TDD §10).
    realtime_enabled: bool = True

    # Rate limits (ADR 052). slowapi-format strings; parsed by the limiter.
    # `rate_limit_enabled` is the global on/off — default on; the local
    # docker-compose dev/E2E stack turns it off so repeated logins/signups in
    # the acceptance suite don't trip the limiter. Production leaves it on.
    rate_limit_enabled: bool = True
    rate_limit_login_per_ip: str = "5/minute"
    rate_limit_login_per_email: str = "10/minute"
    rate_limit_signup_per_ip: str = "3/hour"
    rate_limit_password_reset_per_ip: str = "3/hour"  # noqa: S105
    rate_limit_password_reset_per_email: str = "3/hour"  # noqa: S105
    rate_limit_invites_per_workspace: str = "20/hour"
    rate_limit_authenticated_default: str = "120/minute"

    # Email (ADR 067). `smtp` → MailHog/SMTP in dev; `resend` → Resend HTTP API in
    # prod (swapped from SES in Phase I2). `resend_api_key` is hydrated at boot
    # from the SSM SecureString `/taskflow/prod/resend_api_key` (ADR 073).
    email_backend: Literal["smtp", "resend"] = "smtp"
    email_from: str = "no-reply@taskflow.local"
    email_from_name: str = "TaskFlow"
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    resend_api_key: str | None = None

    # Background jobs / backups (ADR 069, 074).
    scheduler_enabled: bool = True
    s3_backups_bucket: str | None = None
    # AWS region for the S3 backup client (and any future AWS SDK calls). Hydrated
    # from `AWS_REGION` in prod; us-east-1 by default.
    aws_region: str = "us-east-1"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @model_validator(mode="after")
    def _default_cookie_secure(self) -> "Settings":
        # When unset, secure cookies follow the environment: off in dev (so the
        # browser stores them over plain http://localhost), on in production.
        if self.cookie_secure is None:
            self.cookie_secure = self.is_production
        return self


settings = Settings()
