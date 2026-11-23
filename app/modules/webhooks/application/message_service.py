"""MessageService: render content template and deliver via webhook or channel."""
from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.content.infrastructure.repositories import SqlAlchemyContentRepository
from app.modules.webhooks.infrastructure.repositories import SqlAlchemyWebhookRepository
from app.modules.webhooks.infrastructure.services import WebhookSender

logger = logging.getLogger("bot_argon.messages")

PLACEHOLDER_RE = re.compile(r"{([A-Za-z_][A-Za-z0-9_]*)}")


def render_payload(payload: dict[str, Any], variables: dict[str, Any]) -> dict[str, Any]:
    def sub(value: Any) -> Any:
        if isinstance(value, str):
            return PLACEHOLDER_RE.sub(lambda m: str(variables.get(m.group(1), m.group(0))), value)
        if isinstance(value, dict):
            return {k: sub(v) for k, v in value.items()}
        if isinstance(value, list):
            return [sub(v) for v in value]
        return value

    return sub(payload)


class MessageService:
    def __init__(self, factory: async_sessionmaker[AsyncSession], sender: WebhookSender | None = None) -> None:
        self._factory = factory
        self._sender = sender or WebhookSender()

    async def send_event(
        self,
        key: str,
        variables: dict[str, Any] | None = None,
        webhook_name: str | None = None,
        channel: Any | None = None,
    ) -> bool:
        async with self._factory() as session:
            content_repo = SqlAlchemyContentRepository(session)
            template = await content_repo.get(key)
            if template is None:
                logger.warning("Missing content template %s", key)
                return False

            payload = render_payload(template.payload, variables or {})

            webhook_repo = SqlAlchemyWebhookRepository(session)
            if webhook_name:
                webhook = await webhook_repo.get_by_name(webhook_name)
            else:
                webhook = await webhook_repo.first_enabled()

            if webhook is not None:
                return await self._sender.send_embed(webhook.url, payload, color_override=webhook.color)

            if channel is not None:
                try:
                    embed = build_discord_embed(payload)
                    await channel.send(embed=embed)
                    return True
                except Exception:
                    logger.exception("Failed to send message via channel")
                    return False

            logger.warning("No webhook or channel target for template %s", key)
            return False

    async def get_rendered(
        self, key: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        async with self._factory() as session:
            template = await SqlAlchemyContentRepository(session).get(key)
        if template is None:
            return None
        return render_payload(template.payload, variables or {})


def build_discord_embed(payload: dict[str, Any]):
    import discord

    embed = discord.Embed(
        title=payload.get("title"),
        description=payload.get("description"),
        color=payload.get("color") or 0x2B2D31,
    )
    for field in payload.get("fields", []):
        embed.add_field(name=field.get("name", ""), value=field.get("value", ""), inline=field.get("inline", False))
    if payload.get("thumbnail"):
        embed.set_thumbnail(url=payload["thumbnail"])
    if payload.get("image"):
        embed.set_image(url=payload["image"])
    if payload.get("footer"):
        embed.set_footer(text=payload["footer"].get("text", ""))
    return embed

