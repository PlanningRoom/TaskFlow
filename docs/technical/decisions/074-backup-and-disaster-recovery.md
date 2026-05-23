# Decision 074: Backup & Disaster Recovery

**Status:** Decided

**Category:** Ops & Observability

**Question:** How are database backups taken, stored, and restored?

**Options considered:**
- Managed RDS PITR
- Nightly `pg_dump` to S3
- WAL streaming to a secondary
- Combination

**Decision:** Nightly `pg_dump` to S3.

- APScheduler (Decision 069) runs `pg_dump --no-owner --no-privileges` daily at 03:00 UTC; the stdout stream is gzipped in memory before upload (equivalent to `pg_dump … | gzip -9 > taskflow.sql.gz`). Plain-SQL output was chosen over `--format=custom` so the dump is human-readable on `aws s3 cp` and `psql < restore.sql` works without `pg_restore`.
- Dump written to `s3://taskflow-backups-{account}-{region}/backups/YYYY/MM/DD/taskflow-YYYYMMDDTHHMMSSZ.sql.gz`. The intra-day timestamp suffix lets a one-off operator-triggered backup coexist with the nightly run.
- S3 lifecycle rule: retain 30 days, then expire.
- Bucket versioned and encrypted with SSE-S3.
- IAM role on EC2 grants `s3:PutObject` only to this path prefix.

**RPO:** 24 hours. **RTO:** ~1 hour (spin up fresh Postgres container, `aws s3 cp` the dump, `gunzip | psql`).

**Dev posture:** when `S3_BACKUPS_BUCKET` is unset the scheduled job logs `backup.skipped reason=bucket_unset` and returns — `make dev` therefore runs the scheduler without ever shelling out to `pg_dump`.

Restore procedure will be documented in `docs/operations/restore.md` during implementation.

**Rationale:** Running Postgres on EC2 (Decision 033) rules out RDS PITR. A nightly dump is the simplest backup scheme that still gives a meaningful recovery point — appropriate for a demo project where 24h data loss is tolerable. S3 lifecycle keeps storage costs negligible.
