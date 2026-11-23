"""FastAPI dependency that yields a repository per request."""
from typing import AsyncIterator

from database.connection import connect
from database.repository import SqliteRepository


async def get_repository() -> AsyncIterator[SqliteRepository]:
    connection = await connect()
    try:
        yield SqliteRepository(connection)
    finally:
        await connection.close()
