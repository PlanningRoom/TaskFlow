"""Cursor pagination helpers (ADR 040).

Cursor encodes a `(created_at, id)` tuple as URL-safe base64 of
`<iso8601>|<uuid_hex>`. Opaque to clients; ordering is `created_at DESC, id DESC`
unless a phase needs the opposite (comments use `created_at ASC, id ASC` to
display oldest-first).
"""

from __future__ import annotations

import base64
import binascii
from datetime import datetime
from uuid import UUID


def encode_cursor(created_at: datetime, item_id: UUID) -> str:
    raw = f"{created_at.isoformat()}|{item_id.hex}".encode("ascii")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def decode_cursor(encoded: str) -> tuple[datetime, UUID] | None:
    """Inverse of `encode_cursor`. Returns None on malformed input."""
    try:
        padded = encoded + "=" * (-len(encoded) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("ascii")).decode("ascii")
        iso, hex_id = raw.split("|", 1)
        return datetime.fromisoformat(iso), UUID(hex=hex_id)
    except (ValueError, binascii.Error):
        return None
