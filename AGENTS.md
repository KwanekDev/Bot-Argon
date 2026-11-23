# AGENTS.md — Bot Argon

This repository is a Discord bot (discord.py) plus an HTTP API (FastAPI), sharing a
single SQLite database. This file is the source of truth for agents working in this
repository. Read it before making changes.

## Project map

- `bot.py` — Discord bot entrypoint. Sets up intents, logging, `DiscordBot` class,
  database init, and cog loading. Run with `python bot.py` (requires `TOKEN`).
- `cogs/` — Discord command modules. Each cog is one file. Copy `cogs/template.py`
  to add a new cog; register it via `setup(bot)` and it is auto-loaded.
- `database/` — data layer.
  - `schema.sql` — SQLite schema (`warns`, `users`, `api_keys`).
  - `connection.py` — connection helpers (`connect`, `init_schema`, `database_path`).
  - `repository.py` — `BaseRepository` ABC + `SqliteRepository` (data access used by
    both bot and API). Swap backend by implementing `BaseRepository` elsewhere.
- `api/` — FastAPI application.
  - `main.py` — app factory, CORS, lifespan, routers, `/health`.
  - `app/config.py` — pydantic-settings `Settings` (env vars, see `.env.example`).
  - `app/security.py` — Argon2 password hashing, JWT creation/validation, API-key hashing.
  - `app/ratelimit.py` — shared slowapi limiter helper.
  - `app/database.py` — `get_repository` FastAPI dependency.
  - `app/routers/` — `auth.py` (token, me), `warns.py`, `admin.py` (API-key protected).
- `tests/` — pytest + httpx integration tests for the API.
- `.agents/skills/archify/` — Archify skill (interactive architecture diagrams).

## Run

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
copy .env.example .env   # then fill in TOKEN, SECRET_KEY, ...
python bot.py            # Discord bot
uvicorn api.main:app --reload  # API on http://127.0.0.1:8000
```

## API foundations

- `GET /health` — public, rate-limited.
- `POST /api/v1/auth/token` — OAuth2 password flow (form: `username`, `password`) → JWT.
- `GET /api/v1/auth/me` — Bearer token required; returns username/role.
- `GET /api/v1/warns` — Bearer token required; lists warns.
- `GET /api/v1/admin/health` — `X-API-Key` header required; DB connectivity check.

Secrets: `SECRET_KEY`, `TOKEN` live in `.env` (never commit). API keys are stored as
SHA-256 hashes; the raw value is only shown once at creation.

## Conventions

- Python 3.14; async/await everywhere (discord.py + FastAPI).
- Type hints required on all new code. Log via `bot.logger` / standard logging.
- Format with `black`; keep small, focused changes; Conventional Commits for messages.
- SQL changes go into `database/schema.sql` (idempotent `CREATE TABLE IF NOT EXISTS`).

## Archify (mandatory for agents)

Use the bundled Archify skill (`.agents/skills/archify/`) to consult or update the
project's architecture diagrams whenever you change structure, add subsystems, or
need to orient yourself. The skill produces interactive HTML diagrams; do not hand-edit
generated diagrams. After structural changes, regenerate the relevant diagram.

## Security

- Never commit `.env`, `*.db`, `discord.log`, or any credentials — they are gitignored.
- Before pushing, run `python scripts/check-secrets.py` (scans tracked files for secrets).
- GitHub secret scanning with push protection is enabled on the repository.
