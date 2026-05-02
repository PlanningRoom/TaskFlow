#!/usr/bin/env sh
# Container entrypoint: run Alembic to head, then exec the given command.
# Migration failure aborts startup (TDD §7.1 step 3 / §8.4).
set -e

echo "running alembic upgrade head"
alembic upgrade head

exec "$@"
