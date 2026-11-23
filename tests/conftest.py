import os
import secrets
import sys
from pathlib import Path

# Must be set before importing api.main so Settings picks them up.
os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdefghijklmnopqrstuv")
os.environ.setdefault("SLOWAPI_ENABLED", "false")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from api.app.security import hash_api_key, hash_password
from database.connection import connect, init_schema
from database.repository import SqliteRepository


@pytest_asyncio.fixture
async def db_file(tmp_path):
    path = tmp_path / "test.db"
    os.environ["DATABASE_PATH"] = str(path)
    connection = await connect(path)
    raw_key = secrets.token_urlsafe(32)
    try:
        await init_schema(connection)
        repository = SqliteRepository(connection)
        await repository.create_user("admin", hash_password("admin123"), "admin")
        owner = await repository.get_user_by_username("admin")
        await repository.create_api_key("test-key", hash_api_key(raw_key), owner["id"])
    finally:
        await connection.close()
    return path, raw_key


@pytest_asyncio.fixture
async def client(db_file):
    from api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def api_key(db_file):
    _, raw_key = db_file
    return raw_key
