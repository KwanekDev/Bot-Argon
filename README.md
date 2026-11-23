# Bot Argon

Bot Argon to modularny backend oraz bot Discord współdzielące jedną bazę danych, zbudowane według zasad Clean Architecture i Domain-Driven Design. Każda funkcja jest wydzielonym modułem o czterech warstwach (domain → application → infrastructure → presentation), a zależności między modułami prowadzą wyłącznie do wewnątrz.

Projekt składa się z dwóch procesów:

- **API** — FastAPI (async, SQLAlchemy + Alembic),
- **bot Discord** — discord.py, z cogami.

## Spis treści

- [Funkcje](#funkcje)
- [Architektura](#architektura)
- [Szybki start](#szybki-start)
- [Docker](#docker)
- [API](#api)
- [Konfiguracja](#konfiguracja)
- [Testy](#testy)
- [Rozwój](#rozwój)
- [Bezpieczeństwo](#bezpieczeństwo)
- [Licencja](#licencja)

## Funkcje

- **Uwierzytelnianie** — OAuth2 (password flow) → JWT, endpoint `/me`, pełny cykl życia kluczy API (tworzenie, lista, rotacja, odwołanie).
- **System ostrzeżeń (warns)** — encja, use case'y i repozytorium SQLAlchemy; ekspozycja przez `GET /api/v1/warns`.
- **Weryfikacja Roblox** — rozpoczęcie przez `/verify` (kod w About Me) i potwierdzenie przyciskiem; integracja przez `RobloxProfileClient`.
- **Szablony treści** — wszystkie embedy i komunikaty bota pochodzą z `config/seeds/embeds.json`; zarządzanie przez API admina.
- **Webhooki** — magazyn webhooków, wysyłka przez `WebhookSender` (aiohttp) i `MessageService` (szablon → webhook/kanał).
- **Uprawnienia komend** — macierz `command_permissions` (role/uprawnienia), egzekwowana w `gateway.before_invoke`.
- **Bot Discord** — coggi w `presentation/cogs/`; `BotWarnGateway` łączy coggi z modułem warns.

## Architektura

Każdy moduł ma cztery warstwy, a zależności zawsze wskazują do wewnątrz:

```
app/
├── core/                  # fundamenty: settings, database, security, ratelimit…
└── modules/
    ├── authentication/    # domain → application → infrastructure → presentation
    ├── warns/
    ├── verification/
    ├── content/
    ├── webhooks/
    ├── permissions/
    └── discord_bot/
        └── presentation/cogs/   # autoładowane coggi
```

Wspólne elementy znajdują się w `app/core/`: konfiguracja (`settings.py`), sesje bazy danych (`database.py`), seedowanie (`seeds.py`), bezpieczeństwo (`security.py` — Argon2, JWT, hashowanie kluczy API), limitowanie zapytań (`ratelimit.py`), wyjątki i logowanie.

Migracje Alembic oraz seed-y domyślnych szablonów i uprawnień aplikują się automatycznie przy starcie aplikacji.

Interaktywny diagram architektury: `docs/architecture.html`.

## Szybki start

Wymagania: Python 3.14+, pip. Na Windowsie zamiast `python` użyj `.venv/Scripts/python.exe`.

```
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
cp .env.example .env      # uzupełnij TOKEN, SECRET_KEY itd.
```

Uruchomienie bota:

```
python bot.py
```

Uruchomienie API:

```
uvicorn app.app:app --reload
```

Dokumentacja OpenAPI będzie dostępna pod `http://127.0.0.1:8000/docs`.

## Docker

```
docker compose up -d --build
```

Usługa podnosi bota i API, dzieląc wolumen `./database`.

## API

| Metoda | Ścieżka | Opis |
| --- | --- | --- |
| GET | `/health` | Status usługi (publiczny). |
| POST | `/api/v1/auth/token` | OAuth2 password flow (form: username, password) → JWT. |
| GET | `/api/v1/auth/me` | Dane bieżącego użytkownika (Bearer). |
| GET | `/api/v1/warns` | Lista ostrzeżeń (Bearer). |
| GET | `/api/v1/admin/health` | Health check admina (X-API-Key). |
| POST / GET / DELETE | `/api/v1/admin/api-keys[/{id}[/rotate]]` | Cykl życia kluczy API (admin). |
| GET | `/api/v1/admin/content` | Lista szablonów treści. |
| GET / PATCH | `/api/v1/admin/content/{key}` | Odczyt / aktualizacja szablonu. |
| GET / POST / PATCH / DELETE | `/api/v1/admin/webhooks[/{id}]` | Webhooki (w tym zmiana koloru). |
| GET | `/api/v1/admin/permissions` | Macierz uprawnień. |
| GET / PUT | `/api/v1/admin/permissions/{command}` | Uprawnienia konkretnej komendy. |

Klucze API są przechowywane jako hashe SHA-256; surowa wartość jest zwracana tylko raz, przy tworzeniu.

## Konfiguracja

Wszystkie sekrety i ustawienia znajdują się w `.env` (gitignored). Wzorzec: `.env.example`.

Najważniejsze zmienne: `TOKEN`, `PREFIX`, `INVITE_LINK`, `SECRET_KEY`, `API_HOST`, `API_PORT`, `API_CORS_ORIGINS`, `API_RATE_LIMIT`, `SLOWAPI_ENABLED`, `DATABASE_PATH`.

Domyślne szablony treści i uprawnienia: `config/seeds/embeds.json`, `config/seeds/permissions.json` — edytuj te pliki, aby zmienić wartości domyślne.

## Testy

```
pytest
```

Suite używa pytest-asyncio (tryb auto) oraz httpx do testów integracyjnych API.

## Rozwój

- Nowy moduł dodawaj jako `app/modules/<name>/`, zgodnie ze wzorcem czterech warstw.
- Coggi: `app/modules/discord_bot/presentation/cogs/` (ładowane automatycznie).
- Komunikaty i embedy bota zawsze przez szablony treści — nigdy hardcode.
- Zmiany schematu bazy: nowa rewizja Alembic (`alembic revision --autogenerate`) + ewentualne seed-y.
- Formatowanie: `black`; historia commitów: Conventional Commits.

## Bezpieczeństwo

- Nigdy nie commituj `.env`, `*.db`, `discord.log` ani poświadczeń (wszystko w `.gitignore`).
- Przed pushem uruchom: `python scripts/check-secrets.py`.
- W repozytorium włączone jest GitHub secret scanning z push protection.

## Licencja

Projekt jest udostępniony na licencji Apache 2.0 — szczegóły w [`LICENSE.md`](LICENSE.md). Startowy kod bota powstał w oparciu o [Python-Discord-Bot-Template](https://github.com/kkrypt0nn/Python-Discord-Bot-Template) (Apache-2.0).
