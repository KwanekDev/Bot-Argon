"""Seed default content templates and command permissions on startup."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.content.infrastructure.repositories import SqlAlchemyContentRepository
from app.modules.permissions.infrastructure.repositories import (
    SqlAlchemyCommandPermissionRepository,
)

logger = logging.getLogger("bot_argon.seeds")

ROOT = Path(__file__).resolve().parent.parent.parent


async def seed_defaults(factory: async_sessionmaker[AsyncSession]) -> None:
    embeds_path = ROOT / "config" / "seeds" / "embeds.json"
    perms_path = ROOT / "config" / "seeds" / "permissions.json"
    embeds = json.loads(embeds_path.read_text(encoding="utf-8"))
    perms = json.loads(perms_path.read_text(encoding="utf-8"))

    async with factory() as session:
        content_repo = SqlAlchemyContentRepository(session)
        for key, payload in embeds.items():
            if await content_repo.get(key) is None:
                await content_repo.upsert(key, payload)
                logger.info("Seeded content template %s", key)

        perm_repo = SqlAlchemyCommandPermissionRepository(session)
        for command, rule in perms.items():
            if await perm_repo.get(command) is None:
                await perm_repo.upsert(command, rule.get("roles", []), rule.get("permissions", []))
                logger.info("Seeded permissions for command %s", command)

