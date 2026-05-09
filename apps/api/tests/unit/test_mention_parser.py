"""Unit tests for the @mention parser regex (TDD §6.6)."""

from __future__ import annotations

from taskflow.services.mentions import extract_handles


def test_simple_mention() -> None:
    assert extract_handles("Hi @alice") == ["alice"]


def test_punctuated_mention() -> None:
    assert extract_handles("Ping @alice, please") == ["alice"]
    assert extract_handles("@alice. @bob! @carol?") == ["alice", "bob", "carol"]


def test_email_in_body_does_not_extract() -> None:
    handles = extract_handles("Email user@example.com about it")
    assert "example.com" not in handles


def test_dedup_handles() -> None:
    assert extract_handles("@alice @bob @alice") == ["alice", "bob"]


def test_case_normalized() -> None:
    assert extract_handles("@Alice and @ALICE") == ["alice"]


def test_hyphenated_handle() -> None:
    assert extract_handles("@aurora-owner welcome") == ["aurora-owner"]


def test_no_mention() -> None:
    assert extract_handles("nothing here") == []


def test_at_inside_word() -> None:
    assert extract_handles("re@l 2@5") == []
