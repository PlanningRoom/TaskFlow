"""Phase D2 — dispatcher functions in `taskflow.services.emails`."""

from __future__ import annotations

import pytest

from taskflow.services.emails import (
    send_invitation_email,
    send_password_reset_email,
)
from tests.conftest import FakeEmailSender


@pytest.mark.asyncio
async def test_invitation_email_built_correctly(email_sender: FakeEmailSender) -> None:
    await send_invitation_email(
        to="newhire@example.com",
        workspace_name="Aurora Studio",
        inviter_name="Alice Owner",
        raw_token="raw-token-123",
    )
    assert len(email_sender.sent) == 1
    msg = email_sender.sent[0]
    assert msg.to == "newhire@example.com"
    assert msg.template == "invitation"
    assert "Aurora Studio" in msg.subject
    assert "/invitations/raw-token-123" in msg.text_body
    assert "Alice Owner" in msg.text_body


@pytest.mark.asyncio
async def test_password_reset_email_built_correctly(email_sender: FakeEmailSender) -> None:
    await send_password_reset_email(to="user@example.com", raw_token="reset-xyz")
    assert len(email_sender.sent) == 1
    msg = email_sender.sent[0]
    assert msg.to == "user@example.com"
    assert msg.template == "password_reset"
    assert "/reset-password?token=reset-xyz" in msg.text_body


@pytest.mark.asyncio
async def test_invitation_dispatcher_swallows_send_failure(
    email_sender: FakeEmailSender,
) -> None:
    email_sender.raise_on_send = RuntimeError("boom")
    # Should not raise — the user has already received a 200.
    await send_invitation_email(
        to="x@example.com",
        workspace_name="W",
        inviter_name="I",
        raw_token="t",
    )
