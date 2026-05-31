"""Dump the FastAPI OpenAPI schema to JSON, offline (TDD §14.1).

Importing ``taskflow.main`` does not open a database connection — the async
engine is created lazily inside the app lifespan, and ``Settings()`` only reads
env/defaults — so the schema can be generated without booting uvicorn or
Postgres. This backs the frontend type codegen (``packages/api-types``) and the
``openapi-drift`` CI gate.

Usage::

    uv run python -m taskflow.scripts.dump_openapi            # -> stdout
    uv run python -m taskflow.scripts.dump_openapi out.json   # -> file
"""

from __future__ import annotations

import json
import sys

from taskflow.main import app


def render() -> str:
    """Return the app's OpenAPI document as a stable, sorted JSON string."""
    schema = app.openapi()
    # sort_keys keeps the committed artifact deterministic across runs so the
    # drift gate only fires on real contract changes.
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    output = render()
    if len(argv) > 1:
        with open(argv[1], "w", encoding="utf-8") as fh:
            fh.write(output)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
