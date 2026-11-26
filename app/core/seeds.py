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
from app.core.security import hash_password
from app.core.settings import get_settings
from app.modules.authentication.infrastructure.repositories import SqlAlchemyUserRepository
from app.modules.strefa.domain.entities import ApplicationEntity, StrefaCommandEntity
from app.modules.strefa.infrastructure.repositories import (
    SqlAlchemyApplicationRepository,
    SqlAlchemyEventTemplateRepository,
    SqlAlchemyStrefaCommandRepository,
)
from app.modules.discord_bot.infrastructure.flags import SqlAlchemyBotFlagRepository

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

        settings = get_settings()
        admin_username = settings.admin_username
        admin_password = settings.admin_password
        if admin_username and admin_password and not settings.environment.startswith("test"):
            user_repo = SqlAlchemyUserRepository(session)
            existing = await user_repo.get_by_username(admin_username)
            if existing is None:
                await user_repo.create(admin_username, hash_password(admin_password), "admin")
                logger.info("Seeded admin user %s", admin_username)

    await _seed_strefa(factory)
    await _seed_flags(factory)


async def _seed_flags(factory: async_sessionmaker[AsyncSession]) -> None:
    defaults = {
        "presence_activity": "🌲 SCP Strefa Argon RolePlay",
        "presence_type": "0",
        "presence_status": "online",
    }
    async with factory() as session:
        repo = SqlAlchemyBotFlagRepository(session)
        for key, value in defaults.items():
            if await repo.get(key) is None:
                await repo.set(key, value)


async def _seed_strefa(factory: async_sessionmaker[AsyncSession]) -> None:
    source_path = ROOT / "config" / "seeds" / "strefa_source.json"
    if not source_path.exists():
        logger.info("No stefa_source.json; skipping Strefa seed")
        return
    data = json.loads(source_path.read_text(encoding="utf-8"))

    async with factory() as session:
        cmd_repo = SqlAlchemyStrefaCommandRepository(session)
        for raw in data.get("commands", []):
            entity = StrefaCommandEntity(
                name=raw.get("name", ""),
                description=raw.get("description", ""),
                options=raw.get("options", []),
                devonly=bool(raw.get("devonly", False)),
                testonly=bool(raw.get("testonly", False)),
                permissions_required=raw.get("permissionsRequired", []),
                bot_permissions=raw.get("botpermissions", []),
                deleted=bool(raw.get("deleted", False)),
            )
            if entity.name:
                await cmd_repo.upsert(entity)
        logger.info("Seeded %s Strefa commands", len(data.get("commands", [])))

        app_repo = SqlAlchemyApplicationRepository(session)
        # applications are append-only seeds: only add if table empty (avoid dupes)
        existing_apps = await app_repo.list()
        if not existing_apps:
            for raw in data.get("applications", []):
                parent = str(get_settings().strefa_applications_parent_channel or raw.get("parent", ""))
                await app_repo.upsert(ApplicationEntity(
                    name=raw.get("name", ""),
                    parent_channel=parent,
                    send_to=raw.get("sendTo", ""),
                    whitelisted_roles=raw.get("whitelistedroles", []),
                    roles_to_give=raw.get("roletogive", []),
                    questions=raw.get("questions", []),
                ))
            logger.info("Seeded %s applications", len(data.get("applications", [])))

        event_repo = SqlAlchemyEventTemplateRepository(session)
        for raw in data.get("events", []):
            key = raw.get("file", "").replace("\\", "/")
            if key:
                await event_repo.upsert(key, raw)
        logger.info("Seeded %s event templates", len(data.get("events", [])))

