# AGENTS.md — Bot Argon

This repository is a modular backend built on Clean Architecture + DDD (inspired by the
FastAPI Clean Architecture DDD template) that also runs a Discord bot. Every feature is a
module with four layers; dependencies point inward only.

## Project map

- bot.py — Discord bot entrypoint (run: python bot.py with TOKEN set).
- app/app.py — FastAPI application factory (run: uvicorn app.app:app --reload).
- app/core/ — cross-cutting foundations:
  - settings.py — pydantic-settings Settings (env vars, see .env.example).
  - database.py — async SQLAlchemy engine/session factory and Alembic bootstrap.
  - security.py — Argon2 hashing, JWT, API-key hashing.
  - ratelimit.py — slowapi limiter helper.
  - exceptions.py, logging.py — shared primitives.
- app/modules/ — DDD modules, each with domain/ → application/ → infrastructure/ → presentation/:
  - authentication/ — login (OAuth2 form → JWT), /me, API-key lifecycle (create/list/rotate/revoke), admin health.
  - warns/ — warn entity, use cases, SQLAlchemy repository; GET /api/v1/warns.
  - discord_bot/ — bot: cogs live in presentation/cogs/; BotWarnGateway bridges cogs to the warns module.
- migrations/ — Alembic scripts (applied automatically on startup).
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

Migrations apply automatically at app startup via Alembic (alembic upgrade head).

## API

- GET /health — public.
- POST /api/v1/auth/token — OAuth2 password flow (form: username, password) → JWT.
- GET /api/v1/auth/me — Bearer token required.
- GET /api/v1/warns — Bearer token required.
- GET /api/v1/admin/health — X-API-Key header required.
- POST/GET/DELETE /api/v1/admin/api-keys[/{id}[/rotate]] — admin-only API key lifecycle.

Secrets live only in .env (gitignored). API keys are stored as SHA-256 hashes; the raw
value is returned exactly once at creation.

## Conventions

- Python 3.14; async/await everywhere; type hints required.
- Add a new feature as a module under app/modules/<name>/ following the four-layer pattern.
- Cogs: add files under app/modules/discord_bot/presentation/cogs/ (auto-loaded).
- SQL changes: new Alembic revision (alembic revision --autogenerate -m "...").
- Format with black; Conventional Commits.

## Security

- Never commit .env, *.db, discord.log, or credentials — all gitignored.
- Run python scripts/check-secrets.py before pushing.
- GitHub secret scanning with push protection is enabled on the repository.

## Archify (mandatory for agents)

Use the bundled Archify skill (.agents/skills/archify/) to consult or update architecture
diagrams whenever you change structure. The canonical diagram is docs/architecture.html
(source: docs/architecture.architecture.json). Regenerate after structural changes.

