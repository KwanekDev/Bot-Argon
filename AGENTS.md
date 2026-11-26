# AGENTS.md — Bot Argon

This repository is a modular backend built on Clean Architecture + DDD (inspired by the
FastAPI Clean Architecture DDD template) that also runs a Discord bot. Every feature is a
module with four layers; dependencies point inward only.

## Project map

- bot.py — Discord bot entrypoint (run: python bot.py with TOKEN set).
- app/app.py — FastAPI application factory (run: uvicorn app.app:app --reload).
- app/core/ — cross-cutting foundations:
  - settings.py — pydantic-settings Settings (env vars, see .env.example).
  - database.py — async SQLAlchemy engine/session factory, Alembic bootstrap and seeding.
  - seeds.py — seeds default content templates and command permissions from config/seeds/.
  - security.py — Argon2 hashing, JWT, API-key hashing.
  - ratelimit.py — slowapi limiter helper.
  - exceptions.py, logging.py — shared primitives.
- app/modules/ — DDD modules, each with domain/ → application/ → infrastructure/ → presentation/:
  - authentication/ — login (OAuth2 form → JWT), /me, API-key lifecycle (create/list/rotate/revoke), admin health.
  - warns/ — warn entity, use cases, SQLAlchemy repository; GET /api/v1/warns.
  - verification/ — Roblox verification: start (/verify + code in About Me) and confirm (button); RobloxProfileClient (public profile).
  - content/ — content_templates (JSON payloads) for all embeds; CRUD via admin API.
  - webhooks/ — webhooks store, WebhookSender (aiohttp) and MessageService (template → webhook/channel).
  - permissions/ — command_permissions matrix (roles/permissions) enforced in gateway.before_invoke.
  - discord_bot/ — bot: cogs in presentation/cogs/ (obecnie tylko owner.py; verification.py ładuje się z własnego modułu), BotWarnGateway bridges cogs to warns; MessageService for deny messages.
- migrations/ — Alembic scripts (0001 initial, 0002 verification/content/webhooks/permissions; applied+seeded on startup).
- config/seeds/ — embeds.json and permissions.json (edit here to change defaults).
- tests/ — pytest + httpx integration tests.
- scripts/check-secrets.py — secret scanner (run before pushing).
- .agents/skills/archify/ — Archify skill (interactive architecture diagrams).

## Run

    python -m venv .venv
    .venv/Scripts/python.exe -m pip install -r requirements-dev.txt
    copy .env.example .env   # then fill in TOKEN, SECRET_KEY, ...
    python bot.py            # Discord bot
    uvicorn app.app:app --reload  # API on http://127.0.0.1:8000
    pytest                   # run the test suite

Migrations and seed data apply automatically at app startup (Alembic upgrade head + seeds).

## API

- GET /health — public.
- POST /api/v1/auth/token — OAuth2 password flow (form: username, password) → JWT.
- GET /api/v1/auth/me — Bearer token required.
- GET /api/v1/warns — Bearer token required.
- GET /api/v1/admin/health — X-API-Key header required.
- POST/GET/DELETE /api/v1/admin/api-keys[/{id}[/rotate]] — admin-only API key lifecycle.
- GET /api/v1/admin/content, GET/PATCH /api/v1/admin/content/{key} — embed/UI templates (JSON).
- GET /api/v1/admin/webhooks, POST/PATCH/DELETE /api/v1/admin/webhooks[/{id}] — webhooks incl. color change.
- GET /api/v1/admin/permissions, GET/PUT /api/v1/admin/permissions/{command} — command permission matrix.

Secrets live only in .env (gitignored). API keys are stored as SHA-256 hashes; the raw
value is returned exactly once at creation.

## Conventions

- Python 3.14; async/await everywhere; type hints required.
- Add a new feature as a module under app/modules/<name>/ following the four-layer pattern.
- Cogs: add files under app/modules/discord_bot/presentation/cogs/ (auto-loaded).
- All bot-facing messages/embeds come from content_templates (config/seeds/embeds.json); never hardcode.
- SQL changes: new Alembic revision (alembic revision --autogenerate -m "...") + seeds as needed.
- Format with black; Conventional Commits.

## Security

- Never commit .env, *.db, discord.log, or credentials — all gitignored.
- Run python scripts/check-secrets.py before pushing.
- GitHub secret scanning with push protection is enabled on the repository.

## Archify (mandatory for agents)

Use the bundled Archify skill (.agents/skills/archify/) to consult or update architecture
diagrams whenever you change structure. The canonical diagram is docs/architecture.html
(source: docs/architecture.architecture.json). Regenerate after structural changes.

