"""Async SQLAlchemy engine, session factory and bootstrap."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.settings import PROJECT_ROOT, get_settings


class Base(DeclarativeBase):
    pass


_settings = get_settings()
engine = create_async_engine(_settings.database_url, echo=False)
session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


def _run_migrations(url: str) -> None:
    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")


async def init_db() -> None:
    """Apply Alembic migrations to the configured database."""
    await asyncio.to_thread(_run_migrations, _settings.database_url)
    from app.core.seeds import seed_defaults
    await seed_defaults(session_factory)

