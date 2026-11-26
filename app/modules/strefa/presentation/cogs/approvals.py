"""Character/test approval workflow (accept/cancel)."""
import logging

import discord
from discord.ext import commands
from discord.ui import Button, View

from app.modules.strefa import config as C
from app.modules.strefa.presentation.cogs.helpers import build_embed

logger = logging.getLogger("bot_argon.strefa.approvals")

NL = chr(10)

ROLE_KEY = {"character": "accept_characters", "test": "accept_tests"}
LOG_CHANNEL = {"character": "character_logs", "test": "tests_logs"}
DM_TITLE = {
    "character": ("Twoja postać została zatwierdzona!", "Twoja postać została odrzucona!"),
    "test": ("Twój wniosek został zatwierdzony!", "Twój wniosek został odrzucony!"),
}


class ApprovalView(View):
    def __init__(self, kind: str) -> None:
        super().__init__(timeout=None)
        self.kind = kind
        self.add_item(Button(label="Zatwierdź", style=discord.ButtonStyle.success, custom_id=f"approve:{kind}"))
        self.add_item(Button(label="Odrzuć", style=discord.ButtonStyle.danger, custom_id=f"decline:{kind}"))


class Approvals(commands.Cog, name="strefa_approvals"):
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        if interaction.type is not discord.InteractionType.component:
            return
        custom_id = (interaction.data or {}).get("custom_id", "")
        if custom_id in ("approve:character", "approve:test"):
            await self._decide(interaction, custom_id.split(":")[1], approve=True)
        elif custom_id in ("decline:character", "decline:test"):
            await self._decide(interaction, custom_id.split(":")[1], approve=False)

    async def _decide(self, interaction, kind: str, approve: bool) -> None:
        role_key = ROLE_KEY[kind]
        required = C.ROLES.get(role_key)
        if required:
            allowed = {int(required)}
            if not (allowed & {r.id for r in interaction.user.roles}):
                await interaction.response.send_message(C.DENY_MESSAGE, ephemeral=True)
                return

        embed = interaction.message.embeds[0] if interaction.message.embeds else None
        if embed is None:
            return
        applicant_id = _extract(embed)
        if applicant_id is None:
            await interaction.response.send_message("Nie odnaleziono autora wniosku.", ephemeral=True)
            return

        if approve:
            embed.color = C.SUCCESS_GREEN
            embed.set_footer(text=f"Zaakceptowane przez: {interaction.user}", icon_url=C.FOOTER_ICON)
            dm_text = DM_TITLE[kind][0]
        else:
            embed.color = C.FAILURE_RED
            embed.set_footer(text=f"Odrzucone przez: {interaction.user}", icon_url=C.FOOTER_ICON)
            dm_text = DM_TITLE[kind][1] + NL + NL + "* Jeśli uważasz, że to pomyłka, złóż odwołanie."

        await interaction.message.edit(embed=embed, view=None)

        try:
            user = await self.bot.fetch_user(applicant_id)
            dm = build_embed("DEZYZJA", dm_text, C.SUCCESS_GREEN if approve else C.FAILURE_RED)
            await user.send(embed=dm)
        except Exception:
            pass

        log_channel = self.bot.get_channel(int(C.CHANNELS[LOG_CHANNEL[kind]]))
        if log_channel is not None:
            log = build_embed("LOG", f"[Kliknij tutaj]({interaction.message.jump_url})", C.LEADING_COLOR)
            await log_channel.send(embed=log)


def _extract(embed) -> int | None:
    try:
        for field in embed.fields:
            name = field.name.strip()
            if name.startswith("• <@") and name.endswith(">"):
                return int(name[4:-1])
    except Exception:
        pass
    return None


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Approvals())

