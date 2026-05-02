"""Argon2id password hashing (ADR 048)."""

from __future__ import annotations

from taskflow.auth.passwords import hash_password, needs_rehash, verify_password


def test_hash_round_trip() -> None:
    h = hash_password("hunter2-correct-horse")
    assert verify_password("hunter2-correct-horse", h) is True


def test_hash_rejects_wrong_password() -> None:
    h = hash_password("hunter2")
    assert verify_password("wrong", h) is False


def test_hash_returns_argon2id_encoded_string() -> None:
    h = hash_password("anything")
    assert h.startswith("$argon2id$")


def test_two_hashes_differ_due_to_salt() -> None:
    a = hash_password("same")
    b = hash_password("same")
    assert a != b
    assert verify_password("same", a) is True
    assert verify_password("same", b) is True


def test_verify_handles_malformed_hash() -> None:
    assert verify_password("anything", "not-a-real-hash") is False


def test_needs_rehash_false_for_current_params() -> None:
    h = hash_password("any")
    assert needs_rehash(h) is False
