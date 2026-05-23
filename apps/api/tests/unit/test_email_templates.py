"""Phase D2 — Jinja2 template rendering."""

from __future__ import annotations

from html.parser import HTMLParser

from taskflow.adapters.email import render


def _assert_valid_html(html: str) -> None:
    parser = HTMLParser()
    parser.feed(html)
    parser.close()


def test_invitation_template_includes_context() -> None:
    text, html = render(
        "invitation",
        workspace_name="Aurora Studio",
        inviter_name="Alice",
        accept_url="https://taskflow.example/invitations/abc",
    )
    assert "Aurora Studio" in text
    assert "Alice" in text
    assert "https://taskflow.example/invitations/abc" in text
    assert "Aurora Studio" in html
    assert "Alice" in html
    assert 'href="https://taskflow.example/invitations/abc"' in html
    _assert_valid_html(html)


def test_password_reset_template_includes_context() -> None:
    text, html = render(
        "password_reset",
        reset_url="https://taskflow.example/reset-password?token=xyz",
        expires_in_hours=1,
    )
    assert "https://taskflow.example/reset-password?token=xyz" in text
    assert "1 hour" in text  # singular form
    assert "https://taskflow.example/reset-password?token=xyz" in html
    _assert_valid_html(html)


def test_password_reset_pluralises_hours() -> None:
    text, _ = render(
        "password_reset",
        reset_url="https://example/x",
        expires_in_hours=2,
    )
    assert "2 hours" in text
