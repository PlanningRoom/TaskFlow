"""Phase D2 — scheduler job registration."""

from __future__ import annotations

import pytest
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from taskflow.scheduler import init_scheduler, shutdown_scheduler


@pytest.mark.asyncio
async def test_init_scheduler_registers_all_jobs() -> None:
    scheduler = init_scheduler()
    try:
        ids = {job.id for job in scheduler.get_jobs()}
        assert ids == {
            "cleanup.invitations",
            "cleanup.sessions",
            "cleanup.password_resets",
            "backup.pg_dump",
        }

        invitations_job = scheduler.get_job("cleanup.invitations")
        assert isinstance(invitations_job.trigger, IntervalTrigger)

        backup_job = scheduler.get_job("backup.pg_dump")
        assert isinstance(backup_job.trigger, CronTrigger)
        # The CronTrigger string includes the fields; assert hour=3 for backup.
        assert "hour='3'" in str(backup_job.trigger)
    finally:
        shutdown_scheduler(scheduler)
