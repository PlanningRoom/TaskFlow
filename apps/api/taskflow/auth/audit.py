"""In-transaction audit_log writer (ADR 084)."""

from __future__ import annotations

import ipaddress
from typing import Any
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from taskflow.db.models.audit_log import AuditLog


def coerce_ip(value: str | None) -> str | None:
    """Return `value` if it parses as IPv4/IPv6, else None.

    The `audit_log.ip` column is Postgres `inet`; asyncpg rejects non-IP
    strings at insert time. Starlette's `TestClient` for instance uses the
    literal "testclient" as `request.client.host`, which would crash audit
    writes during tests.
    """
    if value is None:
        return None
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return None
    return value


async def write_audit_log(
    db: AsyncSession,
    *,
    event_type: str,
    actor_id: UUID | None = None,
    target_id: UUID | None = None,
    request: Request | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    """Append a row to `audit_log`. Synchronous within the caller's transaction.

    Caller is expected to be inside a transaction; this does not commit.
    """
    ip = None
    user_agent = None
    if request is not None:
        client = request.client
        ip = coerce_ip(client.host) if client else None
        user_agent = request.headers.get("user-agent")

    row = AuditLog(
        actor_id=actor_id,
        event_type=event_type,
        target_id=target_id,
        ip=ip,
        user_agent=user_agent,
        metadata_=metadata or {},
    )
    db.add(row)
    return row
