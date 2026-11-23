"""Central database connection helpers shared by the bot and the API."""
from __future__ import annotations

import os
from pathlib import Path

import aiosqlite

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def database_path() -> Path:
    """Return the configured SQLite database path."""
    override = os.getenv("DATABASE_PATH")
    if override:
        return Path(override)
    return PROJECT_ROOT / "database" / "database.db"


async def connect(database: str | Path | None = None) -> aiosqlite.Connection:
    """Open an aiosqlite connection with the row factory enabled."""
    path = Path(database) if database else database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(path)
    conn.row_factory = aiosqlite.Row
    return conn


async def init_schema(conn: aiosqlite.Connection) -> None:
    """Apply database/schema.sql to the given connection."""
    schema = PROJECT_ROOT / "database" / "schema.sql"
    with open(schema, encoding="utf-8") as f:
        await conn.executescript(f.read())
    await conn.commit()
