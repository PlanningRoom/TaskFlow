"""Transactional email dispatchers (Phase D2).

Both functions are designed to be handed to `BackgroundTasks.add_task` after
the originating request has committed and returned 200. Exceptions are
caught and logged — the user has already received a successful response, so
re-raising would surface a 500 they shouldn't see (TDD §7.4).
"""

from __future__ import annotations

import structlog

from taskflow.adapters.email import EmailMessage, get_email_sender, render
from taskflow.settings import settings

logger = structlog.get_logger(__name__)

# Tracks the password-reset TTL declared in `taskflow.services.auth`; mirrored
# here as a label for the email copy. Kept local so the email module doesn't
# import from auth (avoids a circular import).
_PASSWORD_RESET_EXPIRES_IN_HOURS = 1


async def send_invitation_email(
    *, to: str, workspace_name: str, inviter_name: str, raw_token: str
) -> None:
    accept_url = f"{settings.frontend_base_url.rstrip('/')}/invitations/{raw_token}"
    text, html = render(
        "invitation",
        workspace_name=workspace_name,
        inviter_name=inviter_name,
        accept_url=accept_url,
    )
    msg = EmailMessage(
        to=to,
        subject=f"You're invited to {workspace_name} on TaskFlow",
        text_body=text,
        html_body=html,
        template="invitation",
    )
    try:
        await get_email_sender().send(msg)
    except Exception:
        # Already logged by the adapter; swallow so BackgroundTasks doesn't crash the worker.
        logger.warning("email.dispatch.dropped", template="invitation", to=to)


async def send_password_reset_email(*, to: str, raw_token: str) -> None:
    reset_url = f"{settings.frontend_base_url.rstrip('/')}/reset-password?token={raw_token}"
    text, html = render(
        "password_reset",
        reset_url=reset_url,
        expires_in_hours=_PASSWORD_RESET_EXPIRES_IN_HOURS,
    )
    msg = EmailMessage(
        to=to,
        subject="Reset your TaskFlow password",
        text_body=text,
        html_body=html,
        template="password_reset",
    )
    try:
        await get_email_sender().send(msg)
    except Exception:
        logger.warning("email.dispatch.dropped", template="password_reset", to=to)
