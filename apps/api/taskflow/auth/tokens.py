"""Random token primitives (ADR 047, 049, 051) — `secrets`-backed."""

from __future__ import annotations

import hashlib
import secrets


def generate_token(num_bytes: int = 32) -> tuple[str, bytes]:
    """Return (raw_url_safe_token, sha256_hash_bytes)."""
    raw = secrets.token_urlsafe(num_bytes)
    return raw, hash_token(raw)


def hash_token(raw: str) -> bytes:
    return hashlib.sha256(raw.encode("ascii")).digest()
