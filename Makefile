.PHONY: dev down migrate revision seed test e2e e2e-up e2e-install lint typecheck cfn-lint build install bootstrap lock

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

e2e-install:
	pnpm --filter @taskflow/e2e exec playwright install --with-deps chromium

# Boot the full dev stack detached, wait for the API + web to answer, then seed.
# Run this once, then `make e2e` against the running stack.
e2e-up: bootstrap
	docker compose up -d --build
	@echo "Waiting for api (:8000/health) and web (:5173)…"
	@timeout=180; until curl -fsS http://localhost:8000/health >/dev/null 2>&1; do \
		timeout=$$((timeout-2)); [ $$timeout -le 0 ] && echo "api never became healthy" && exit 1; sleep 2; done
	@timeout=180; until curl -fsS http://localhost:5173 >/dev/null 2>&1; do \
		timeout=$$((timeout-2)); [ $$timeout -le 0 ] && echo "web never came up" && exit 1; sleep 2; done
	$(MAKE) seed
	@echo "Stack ready. Run: make e2e"

e2e:
	pnpm --filter @taskflow/e2e exec playwright test

lint:
	pnpm exec biome check .
	docker compose run --rm api ruff check .
	docker compose run --rm api ruff format --check .

typecheck:
	pnpm exec tsc -b
	docker compose run --rm api mypy taskflow

cfn-lint:
	uvx cfn-lint infra/cloudformation/*.yml

build:
	docker compose -f docker-compose.prod.yml build
