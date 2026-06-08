# TaskFlow — Local Development Startup

How to run the app locally on macOS / Apple Silicon for manual testing.

> **Key gotcha:** the Docker `web` container does **not** work on this
> machine — `pnpm install` inside the node-alpine container crashes with
> `ERR_PNPM_Unknown system error -35` (EAGAIN) over the bind mount. So we
> run the **backend in Docker** and **Vite on the host**. Everything below
> assumes that split.

## 1. Start the backend (Docker)

```bash
# from the repo root
docker compose up -d db mailhog api
docker compose stop web        # free port 5173 for host Vite
```

Wait for the API to come up (the db is gated on a healthcheck, so the
first request may 000 once before it answers):

```bash
curl -s -w ' [%{http_code}]\n' http://localhost:8000/health   # -> {"status":"ok"} [200]
```

| Service | URL | Notes |
|---|---|---|
| API | http://localhost:8000 | `/health`, `/api/v1/openapi.json` |
| MailHog | http://localhost:8025 | catches all dev email (invites, password resets) |
| Postgres | localhost:5432 | data persists across `down` (volume) |

MailHog runs under emulation (amd64 image on arm64) and logs a harmless
platform warning on start.

## 2. Start the frontend (host Vite)

```bash
pnpm --filter @taskflow/web dev      # -> http://localhost:5173
```

Vite proxies `/api` and `/ws` to `localhost:8000` (see
`apps/web/vite.config.ts`), so it's same-origin and auth cookies flow.

Quick proxy check (should be 401 when logged out, not a connection error):

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:5173/api/v1/auth/me
```

## 3. Seed data & login

The seed script is idempotent; if the DB is empty, run `make seed`.

- **Login:** `owner@aurora.example.com` / `correct-horse-battery-staple`
- Other seeded roles use the same `@aurora.example.com` domain (see
  `apps/api/taskflow/scripts/seed.py` / README for the full list).

> Re-seeding with **new** emails needs a clean DB:
> `docker compose down -v && docker compose up -d db && make seed`.

### Why these specific values (history)

Local browser login was broken after Phase G1 and fixed on `main`
2026-05-31. Three things to know so they don't regress:

1. **Cookies are non-Secure in dev** — derived from `APP_ENV` in
   `apps/api/taskflow/settings.py`. Browsers won't store `Secure` cookies
   over plain `http://localhost`.
2. **CSRF cookie is `taskflow_csrf`** — frontend (`apps/web/src/api/client.ts`)
   and backend agree on this name.
3. **Seed emails use `@aurora.example.com`**, not a reserved `.test` TLD
   (which `email-validator` rejects with a 422). Do not relax `EmailStr`.

## 4. Shut down

```bash
# stop the host Vite process (Ctrl-C in its terminal)
docker compose down          # keeps the Postgres volume + seed data
# docker compose down -v     # also wipes the DB
```
