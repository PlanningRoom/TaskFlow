# TaskFlow API

FastAPI backend for TaskFlow. See the root `README.md` and `docs/technical/technical-design-document.md` for the full picture.

## Local development

The API is meant to run via the root `docker compose` stack:

```
make dev
```

To run it natively for fast iteration:

```
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn taskflow.main:app --reload
```
