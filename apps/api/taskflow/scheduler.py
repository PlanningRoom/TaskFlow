"""In-process APScheduler (ADR 069 / TDD §7.4).

Owns four jobs:

| Job                                | Trigger              |
|------------------------------------|----------------------|
| expire_invitations                 | every 15 minutes     |
| delete_expired_sessions            | daily 04:00 UTC      |
| delete_expired_password_reset_tokens | daily 04:00 UTC    |
| backup_database_to_s3              | daily 03:00 UTC      |

All jobs run with `coalesce=True, max_instances=1` so missed windows don't
pile up duplicates after a restart.
"""

from __future__ import annotations

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from taskflow.services import cleanup

logger = structlog.get_logger(__name__)


def init_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        cleanup.expire_invitations,
        trigger=IntervalTrigger(minutes=15),
        id="cleanup.invitations",
        coalesce=True,
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup.delete_expired_sessions,
        trigger=CronTrigger(hour=4, minute=0, timezone="UTC"),
        id="cleanup.sessions",
        coalesce=True,
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup.delete_expired_password_reset_tokens,
        trigger=CronTrigger(hour=4, minute=0, timezone="UTC"),
        id="cleanup.password_resets",
        coalesce=True,
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup.backup_database_to_s3,
        trigger=CronTrigger(hour=3, minute=0, timezone="UTC"),
        id="backup.pg_dump",
        coalesce=True,
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "scheduler.started",
        jobs=[j.id for j in scheduler.get_jobs()],
    )
    return scheduler


def shutdown_scheduler(scheduler: AsyncIOScheduler | None) -> None:
    if scheduler is None:
        return
    scheduler.shutdown(wait=False)
    logger.info("scheduler.shutdown")
