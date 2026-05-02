"""Token primitives (ADR 047 / 049 / 051)."""

from __future__ import annotations

from taskflow.auth.tokens import generate_token, hash_token


def test_generate_token_yields_url_safe_string_and_hash() -> None:
    raw, h = generate_token(32)
    assert isinstance(raw, str)
    assert isinstance(h, bytes)
    assert len(h) == 32  # SHA-256
    # url-safe alphabet only.
    assert all(c.isalnum() or c in "-_" for c in raw)


def test_generate_token_pairs_are_unique() -> None:
    a, _ = generate_token()
    b, _ = generate_token()
    assert a != b


def test_hash_token_is_deterministic() -> None:
    raw = "fixed"
    assert hash_token(raw) == hash_token(raw)
