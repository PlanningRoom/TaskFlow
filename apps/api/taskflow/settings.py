from typing import Literal

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
    csrf_cookie_name: str = "csrf_token"
    csrf_header_name: str = "X-CSRF-Token"
    session_idle_ttl_days: int = 7
    session_absolute_ttl_days: int = 30
    cookie_secure: bool = True  # Override to false in pure-localhost dev if needed.

    # Real-time fan-out (ADR 044, 045; TDD §10).
    realtime_enabled: bool = True

    # Rate limits (ADR 052). slowapi-format strings; parsed by the limiter.
    rate_limit_login_per_ip: str = "5/minute"
    rate_limit_login_per_email: str = "10/minute"
    rate_limit_signup_per_ip: str = "3/hour"
    rate_limit_password_reset_per_ip: str = "3/hour"  # noqa: S105
    rate_limit_password_reset_per_email: str = "3/hour"  # noqa: S105
    rate_limit_invites_per_workspace: str = "20/hour"
    rate_limit_authenticated_default: str = "120/minute"

    # Email (ADR 067). `smtp` → MailHog/SMTP in dev; `ses` → Amazon SES in prod.
    email_backend: Literal["smtp", "ses"] = "smtp"
    email_from: str = "no-reply@taskflow.local"
    email_from_name: str = "TaskFlow"
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    ses_region: str = "us-east-1"

    # Background jobs / backups (ADR 069, 074).
    scheduler_enabled: bool = True
    s3_backups_bucket: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


settings = Settings()
