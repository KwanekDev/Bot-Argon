"""Repository layer.

Provides a single data-access interface shared by the bot and the API.
The concrete implementation uses SQLite (aiosqlite); a future PostgreSQL
implementation can implement the same BaseRepository interface without
changing callers.
"""
from __future__ import annotations

import abc
from typing import Any

import aiosqlite


class BaseRepository(abc.ABC):
    """Abstract data-access contract."""

    @abc.abstractmethod
    async def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        """Return a user row by username or None."""

    @abc.abstractmethod
    async def create_user(
        self, username: str, password_hash: str, role: str = "user"
    ) -> int:
        """Create a user and return its id."""

    @abc.abstractmethod
    async def get_api_key_by_hash(self, key_hash: str) -> dict[str, Any] | None:
        """Return an API key row by its SHA-256 hash or None."""

    @abc.abstractmethod
    async def create_api_key(self, name: str, key_hash: str, owner_id: int) -> int:
        """Create an API key and return its id."""

    @abc.abstractmethod
    async def list_warns(
        self, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """List warns ordered by newest first."""

    @abc.abstractmethod
    async def ping(self) -> None:
        """Execute a trivial query to verify connectivity."""


class SqliteRepository(BaseRepository):
    """SQLite implementation backed by an aiosqlite connection."""

    def __init__(self, connection: aiosqlite.Connection) -> None:
        self._conn = connection

    async def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        cursor = await self._conn.execute(
            "SELECT id, username, password_hash, role, created_at FROM users WHERE username = ?",
            (username,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def create_user(
        self, username: str, password_hash: str, role: str = "user"
    ) -> int:
        cursor = await self._conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        await self._conn.commit()
        return int(cursor.lastrowid)

    async def get_api_key_by_hash(self, key_hash: str) -> dict[str, Any] | None:
        cursor = await self._conn.execute(
            "SELECT id, name, key_hash, owner_id, scopes, created_at FROM api_keys WHERE key_hash = ?",
            (key_hash,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def create_api_key(self, name: str, key_hash: str, owner_id: int) -> int:
        cursor = await self._conn.execute(
            "INSERT INTO api_keys (name, key_hash, owner_id) VALUES (?, ?, ?)",
            (name, key_hash, owner_id),
        )
        await self._conn.commit()
        return int(cursor.lastrowid)

    async def list_warns(
        self, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        cursor = await self._conn.execute(
            "SELECT id, user_id, server_id, moderator_id, reason, created_at "
            "FROM warns ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def ping(self) -> None:
        await self._conn.execute("SELECT 1")
