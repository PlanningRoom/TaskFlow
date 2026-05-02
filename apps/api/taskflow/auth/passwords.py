"""Argon2id password hashing (ADR 048)."""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# OWASP-tuned for ~300-500ms on a t4g.small (ADR 048).
_HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)


def hash_password(plain: str) -> str:
    """Hash a plaintext password. Returns an encoded Argon2id string."""
    return _HASHER.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time verify. Returns False on mismatch (no exception leaks)."""
    try:
        return _HASHER.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        # Malformed hash, missing parameters, etc. Treat as a mismatch.
        return False


def needs_rehash(hashed: str) -> bool:
    """True if the hash uses parameters below the current floor (ADR 048)."""
    try:
        return _HASHER.check_needs_rehash(hashed)
    except Exception:
        return True
