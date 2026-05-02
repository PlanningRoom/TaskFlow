.PHONY: dev down migrate revision seed test e2e lint typecheck build install bootstrap lock

bootstrap:
	@if [ ! -f .env.local ]; then cp .env.example .env.local; echo "Created .env.local from .env.example"; fi

install:
	pnpm install
	cd apps/api && uv sync

lock:
	cd apps/api && uv lock

dev: bootstrap
	docker compose up

down:
	docker compose down

migrate:
	docker compose run --rm api alembic upgrade head

revision:
	@if [ -z "$$m" ]; then echo "Usage: make revision m=\"message\""; exit 1; fi
	docker compose run --rm api alembic revision --autogenerate -m "$$m"

seed:
	docker compose run --rm api python -m taskflow.scripts.seed

test:
	docker compose -f docker-compose.test.yml run --rm api-test
	pnpm --filter @taskflow/web test --run || true

e2e:
	pnpm exec playwright test

lint:
	pnpm exec biome check .
	docker compose run --rm api ruff check .
	docker compose run --rm api ruff format --check .

typecheck:
	pnpm exec tsc -b
	docker compose run --rm api mypy taskflow

build:
	docker compose -f docker-compose.prod.yml build
