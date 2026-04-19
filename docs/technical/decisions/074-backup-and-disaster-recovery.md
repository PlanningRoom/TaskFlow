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

- APScheduler (Decision 069) runs `pg_dump --format=custom --compress=9` daily at 03:00 UTC.
- Dump written to `s3://taskflow-backups-{account}-{region}/postgres/YYYY-MM-DD/taskflow.dump`.
- S3 lifecycle rule: retain 30 days, then expire.
- Bucket versioned and encrypted with SSE-S3.
- IAM role on EC2 grants `s3:PutObject` only to this path prefix.

**RPO:** 24 hours. **RTO:** ~1 hour (spin up fresh Postgres container, `aws s3 cp` the dump, `pg_restore`).

Restore procedure will be documented in `docs/operations/restore.md` during implementation.

**Rationale:** Running Postgres on EC2 (Decision 033) rules out RDS PITR. A nightly dump is the simplest backup scheme that still gives a meaningful recovery point — appropriate for a demo project where 24h data loss is tolerable. S3 lifecycle keeps storage costs negligible.
