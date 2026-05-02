"""UUIDv7 generator (TDD §8.2).

Wraps `uuid_utils.uuid7()` and returns a stdlib `uuid.UUID` so SQLAlchemy /
Pydantic see the canonical type.
"""

from __future__ import annotations

from uuid import UUID

import uuid_utils


def uuid7() -> UUID:
    """Return a UUIDv7 as a stdlib `uuid.UUID`."""
    return UUID(str(uuid_utils.uuid7()))
