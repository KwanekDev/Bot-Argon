import asyncio
import os
import secrets
import sys
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdefghijklmnopqrstuv")
os.environ.setdefault("SLOWAPI_ENABLED", "false")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def run_migrations(url: str) -> None:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")


@pytest_asyncio.fixture
async def db_file(tmp_path):
    from app.core.security import hash_api_key, hash_password
    from app.modules.authentication.infrastructure.repositories import (
        SqlAlchemyApiKeyRepository,
        SqlAlchemyUserRepository,
    )
    from app.modules.warns.infrastructure.repositories import SqlAlchemyWarnRepository

    path = tmp_path / "test.db"
    url = f"sqlite+aiosqlite:///{path}"
    os.environ["DATABASE_PATH"] = str(path)
    await asyncio.to_thread(run_migrations, url)

    engine = create_async_engine(url)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with factory() as session:
        users = SqlAlchemyUserRepository(session)
        await users.create("admin", hash_password("admin123"), "admin")
        owner = await users.get_by_username("admin")
        raw_key = secrets.token_urlsafe(32)
        keys = SqlAlchemyApiKeyRepository(session)
        await keys.create("test-key", hash_api_key(raw_key), owner.id)
        warns = SqlAlchemyWarnRepository(session)
        await warns.add(111, 222, 333, "test warn")

    return url, factory, raw_key


@pytest_asyncio.fixture
async def client(db_file):
    from app.app import app
    from app.core.database import get_session

    _, factory, _ = db_file

    async def override_get_session():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def api_key(db_file):
    return db_file[2]

