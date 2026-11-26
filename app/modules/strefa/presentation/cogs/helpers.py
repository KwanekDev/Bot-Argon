"""Shared embed helpers for Strefa."""
import datetime

import discord

from app.core.database import session_factory
from app.modules.content.infrastructure.repositories import SqlAlchemyContentRepository
from app.modules.strefa import config as C
from app.modules.webhooks.application.message_service import render_payload


def build_embed(title: str, description: str, color: int, fields=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    embed.set_footer(text=C.FOOTER_TEXT, icon_url=C.FOOTER_ICON)
    for name, value in (fields or []):
        embed.add_field(name=name, value=value, inline=False)
    return embed


async def send_public(target, embed, content=None):
    if isinstance(target, discord.Interaction):
        msg = await target.followup.send(content=content, embed=embed)
        return msg
    return await target.send(content=content, embed=embed)


async def send_ephemeral(target, message: str) -> None:
    if isinstance(target, discord.Interaction):
        try:
            await target.followup.send(message, ephemeral=True)
            return
        except Exception:
            pass
        await target.channel.send(message)
    else:
        await target.send(message)


async def load_template(key: str, variables=None):
    async with session_factory() as session:
        tpl = await SqlAlchemyContentRepository(session).get(key)
    if tpl is None:
        return None
    return render_payload(tpl.payload, variables or {})


def apply_payload(embed, payload):
    if not payload:
        return embed
    if payload.get("title"):
        embed.title = payload["title"]
    if payload.get("description") is not None:
        embed.description = payload["description"]
    if payload.get("color") is not None:
        embed.color = payload["color"]
    embed.clear_fields()
    for f in payload.get("fields", []):
        embed.add_field(name=f.get("name", ""), value=f.get("value", ""), inline=f.get("inline", False))
    return embed


async def send_channel_log(bot, key: str, title: str, description: str) -> bool:
    channel_id = C.CHANNELS.get(key)
    if not channel_id:
        return False
    channel = bot.get_channel(int(channel_id))
    if channel is None:
        return False
    await channel.send(embed=build_embed(title, description, C.LEADING_COLOR))
    return True

