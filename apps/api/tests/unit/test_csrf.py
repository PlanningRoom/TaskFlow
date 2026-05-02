"""CSRF double-submit verification (ADR 051, TDD §8.2 / §11.3)."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import cast

from taskflow.auth.csrf import csrf_check
from taskflow.auth.sessions import encode_csrf
from taskflow.db.models.session import Session as SessionModel


@dataclass
class _FakeSession:
    csrf_token: bytes


def _session_pair() -> tuple[SessionModel, str]:
    raw = secrets.token_bytes(32)
    return cast(SessionModel, _FakeSession(csrf_token=raw)), encode_csrf(raw)


def test_get_bypasses_csrf() -> None:
    assert csrf_check("GET", header_token=None, cookie_token=None, session=None) is True
    assert csrf_check("HEAD", header_token=None, cookie_token=None, session=None) is True
    assert csrf_check("OPTIONS", header_token=None, cookie_token=None, session=None) is True


def test_post_with_matching_tokens_passes() -> None:
    session, token = _session_pair()
    assert csrf_check("POST", header_token=token, cookie_token=token, session=session) is True


def test_post_missing_header_fails() -> None:
    session, token = _session_pair()
    assert csrf_check("POST", header_token=None, cookie_token=token, session=session) is False


def test_post_missing_cookie_fails() -> None:
    session, token = _session_pair()
    assert csrf_check("POST", header_token=token, cookie_token=None, session=session) is False


def test_post_token_mismatch_fails() -> None:
    session, _token = _session_pair()
    other = encode_csrf(secrets.token_bytes(32))
    assert csrf_check("POST", header_token=other, cookie_token="abc", session=session) is False


def test_post_session_csrf_mismatch_fails() -> None:
    # Header and cookie agree, but session has a different bound value.
    session_a, _token_a = _session_pair()
    _session_b, token_b = _session_pair()
    assert (
        csrf_check("POST", header_token=token_b, cookie_token=token_b, session=session_a) is False
    )


def test_post_without_session_fails() -> None:
    _session, token = _session_pair()
    assert csrf_check("PATCH", header_token=token, cookie_token=token, session=None) is False


def test_post_malformed_base64_fails() -> None:
    session, _token = _session_pair()
    junk = "!!!not-base64!!!"
    assert csrf_check("POST", header_token=junk, cookie_token=junk, session=session) is False


def test_methods_other_than_safe_check() -> None:
    session, token = _session_pair()
    for method in ("PATCH", "PUT", "DELETE"):
        assert csrf_check(method, header_token=None, cookie_token=None, session=session) is False
        assert csrf_check(method, header_token=token, cookie_token=token, session=session) is True
