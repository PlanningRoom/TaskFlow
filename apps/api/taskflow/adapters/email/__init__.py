"""Email adapter package (ADR 067).

`get_email_sender()` returns the singleton selected by `settings.email_backend`.
`render(...)` renders a Jinja2 template pair into `(text, html)`.
Tests override the sender via `set_email_sender(...)`.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from taskflow.adapters.email.base import EmailMessage, EmailSender
from taskflow.settings import settings

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_jinja = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(enabled_extensions=("html",), default_for_string=False),
    keep_trailing_newline=True,
)

_sender: EmailSender | None = None


def render(template: str, /, **ctx: object) -> tuple[str, str]:
    """Return `(text_body, html_body)` for the named template pair."""
    text = _jinja.get_template(f"{template}.txt").render(**ctx)
    html = _jinja.get_template(f"{template}.html").render(**ctx)
    return text, html


def get_email_sender() -> EmailSender:
    global _sender
    if _sender is None:
        if settings.email_backend == "resend":
            from taskflow.adapters.email.resend import ResendEmailSender

            _sender = ResendEmailSender()
        else:
            from taskflow.adapters.email.smtp import SmtpEmailSender

            _sender = SmtpEmailSender()
    return _sender


def set_email_sender(sender: EmailSender | None) -> None:
    """Test hook — inject a fake sender, or pass None to force re-resolution."""
    global _sender
    _sender = sender


__all__ = [
    "EmailMessage",
    "EmailSender",
    "get_email_sender",
    "render",
    "set_email_sender",
]
