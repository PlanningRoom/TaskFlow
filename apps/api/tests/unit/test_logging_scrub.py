"""Phase E2 — PII scrubbing processor."""

from __future__ import annotations

from taskflow.logging_config import scrub_pii


def test_top_level_pii_keys_redacted() -> None:
    out = scrub_pii(None, "info", {"email": "a@b.com", "name": "Alice"})
    assert out["email"] == "[REDACTED]"
    assert out["name"] == "[REDACTED]"


def test_non_pii_keys_untouched() -> None:
    out = scrub_pii(None, "info", {"event": "auth.login.success", "user_id": "abc"})
    assert out == {"event": "auth.login.success", "user_id": "abc"}


def test_nested_dict_redacted() -> None:
    event_dict = {
        "event": "workspace.invitation.sent",
        "metadata": {"email": "newhire@example.com", "role": "member"},
    }
    out = scrub_pii(None, "info", event_dict)
    assert out["metadata"]["email"] == "[REDACTED]"
    assert out["metadata"]["role"] == "member"


def test_list_of_dicts_redacted() -> None:
    event_dict = {
        "event": "members.bulk",
        "members": [{"name": "Alice", "id": "1"}, {"name": "Bob", "id": "2"}],
    }
    out = scrub_pii(None, "info", event_dict)
    assert out["members"][0]["name"] == "[REDACTED]"
    assert out["members"][1]["name"] == "[REDACTED]"
    assert out["members"][0]["id"] == "1"


def test_passwords_redacted() -> None:
    out = scrub_pii(
        None,
        "info",
        {"password": "p", "current_password": "c", "new_password": "n"},
    )
    assert out["password"] == "[REDACTED]"
    assert out["current_password"] == "[REDACTED]"
    assert out["new_password"] == "[REDACTED]"


def test_markdown_bodies_redacted() -> None:
    out = scrub_pii(None, "info", {"description": "task desc", "body": "comment body"})
    assert out["description"] == "[REDACTED]"
    assert out["body"] == "[REDACTED]"
