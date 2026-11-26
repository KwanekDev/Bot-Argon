"""Welcome, boost and presence."""
import datetime

import discord
from discord.ext import commands

from app.core.database import session_factory
from app.modules.discord_bot.infrastructure.flags import SqlAlchemyBotFlagRepository
from app.modules.strefa import config as C
from app.modules.strefa.infrastructure.repositories import SqlAlchemyEventTemplateRepository
from app.modules.strefa.infrastructure.render import build_event_output
from app.modules.strefa.presentation.cogs.helpers import build_embed
from app.modules.strefa.presentation.cogs.helpers import apply_payload, load_template

WELCOME_KEY = "guildMemberAdd/welcomeMessage.js"
BOOST_KEY = "messageCreate/boostDetection.js"


class StrefaEvents(commands.Cog, name="strefa_events"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _template(self, key: str):
        async with session_factory() as session:
            return await SqlAlchemyEventTemplateRepository(session).get(key)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("DBG: EVENTS on_ready", flush=True)
        async with session_factory() as session:
            flags = SqlAlchemyBotFlagRepository(session)
            act = await flags.get("presence_activity") or C.ACTIVITY
            atype = int(await flags.get("presence_type") or 0)
            status = (await flags.get("presence_status") or "online").lower()
        activity = discord.Activity(type=discord.ActivityType(atype), name=act)
        await self.bot.change_presence(status=discord.Status(status), activity=activity)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.bot:
            return
        payload = await self._template(WELCOME_KEY)
        if not payload:
            return
        out = build_event_output(payload, {"member.user": member.mention, "member": member})
        embed = discord.Embed(color=C.LEADING_COLOR, timestamp=datetime.datetime.now(datetime.timezone.utc))
        embed.description = out["embed"].get("description", "")
        icon = out["embed"].get("footer", {}).get("icon_url")
        if icon:
            embed.set_footer(text=C.FOOTER_TEXT, icon_url=icon)
        elif out["embed"].get("footer"):
            embed.set_footer(text=out["embed"]["footer"].get("text", C.FOOTER_TEXT))
        embed.set_thumbnail(url=member.display_avatar.url)
        tpl = await load_template("strefa.welcome")
        embed = apply_payload(embed, tpl)
        content = out["content"] or f"||{member.mention}||"
        channel = self.bot.get_channel(int(C.CHANNELS["welcome"]))
        if channel is not None:
            await channel.send(content=content, embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        boost_channel = C.SETTINGS.strefa_boost_channel
        if not boost_channel or str(message.channel.id) != boost_channel:
            return
        payload = await self._template(BOOST_KEY)
        if not payload:
            return
        out = build_event_output(payload, {"member.user": message.author.mention})
        embed = discord.Embed(color=C.LEADING_COLOR, timestamp=datetime.datetime.now(datetime.timezone.utc))
        embed.description = out["embed"].get("description", "")
        icon = out["embed"].get("footer", {}).get("icon_url")
        if icon:
            embed.set_footer(text=C.FOOTER_TEXT, icon_url=icon)
        tpl = await load_template("strefa.boost")
        embed = apply_payload(embed, tpl)
        await message.channel.send(content=out.get("content") or None, embed=embed)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StrefaEvents(bot))
