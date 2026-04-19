# Decision 048: Password Hashing Algorithm

**Status:** Decided

**Category:** Auth Implementation

**Question:** Which algorithm hashes user passwords at rest?

**Options considered:**
- Argon2id
- bcrypt
- scrypt

**Decision:** Argon2id via the `argon2-cffi` library. Parameters: `time_cost=3`, `memory_cost=65536` (64 MB), `parallelism=4`. Tuned for ~300–500 ms on a `t4g.small` — sufficient per OWASP guidance without starving the rest of the app on a 2 GB-RAM instance.

**Rationale:** Argon2id is the current OWASP-recommended default. `argon2-cffi` is the canonical Python binding. Parameters are tunable in config and should be reviewed annually. Hashes include the parameters inline so future re-tuning does not invalidate existing credentials — on login, we rehash if the stored params are below the current floor.
