"""Roblox verification cog: static embed + button + modal flow."""
import logging

import discord
from discord.ext import commands
from discord.ui import Button, Modal, TextInput, View

from app.core.database import session_factory
from app.core.settings import get_settings
from app.modules.discord_bot.infrastructure.flags import SqlAlchemyBotFlagRepository
from app.modules.verification.application.use_cases import VerificationUseCases
from app.modules.verification.domain.enums import VerificationStatus
from app.modules.verification.infrastructure.roblox_client import RobloxProfileClient
from app.modules.verification.infrastructure.repositories import SqlAlchemyVerificationRepository
from app.modules.webhooks.application.message_service import MessageService, build_discord_embed

logger = logging.getLogger("bot_argon.verification")

STATIC_FLAG = "verify_static_sent"

STATUS_KEYS = {
    VerificationStatus.SUCCESS: "verify.success",
    VerificationStatus.FAIL_CODE: "verify.fail_code",
    VerificationStatus.FAIL_NOTFOUND: "verify.fail_notfound",
    VerificationStatus.FAIL_EXPIRED: "verify.fail_expired",
    VerificationStatus.ALREADY_LINKED: "verify.already_linked",
    VerificationStatus.NO_PENDING: "verify.start",
}


class VerifyModal(Modal):
    def __init__(self, cog: "Verification") -> None:
        super().__init__(title="Weryfikacja konta Roblox")
        self.cog = cog
        self.add_item(
            TextInput(
                label="Twój ID na Robloxie",
                placeholder="np. 123456789",
                min_length=1,
                max_length=20,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        roblox_id = self.children[0].value.strip()
        discord_id = str(interaction.user.id)

        async with session_factory() as session:
            repo = SqlAlchemyVerificationRepository(session)
            existing = await repo.get_link_by_discord(discord_id)
        if existing is not None:
            await interaction.response.send_message(
                "Masz już powiązane konto Roblox.", ephemeral=True
            )
            return

        async with session_factory() as session:
            repo = SqlAlchemyVerificationRepository(session)
            use_cases = VerificationUseCases(repo, RobloxProfileClient())
            code = await use_cases.start(discord_id, roblox_id)

        payload = await self.cog.messages.get_rendered(
            "verify.start", {"code": code, "roblox_id": roblox_id}
        )
        embed = build_discord_embed(payload or {"description": "Błąd."})
        view = ConfirmView()

        try:
            await interaction.user.send(embed=embed, view=view)
            await interaction.response.send_message(
                "Sprawdź prywatną wiadomość od bota.", ephemeral=True
            )
        except Exception:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ConfirmView(View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(Button(label="Potwierdzam", style=discord.ButtonStyle.success, custom_id="verify:confirm"))


class StaticVerifyView(View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(Button(label="Rozpocznij weryfikację", style=discord.ButtonStyle.success, custom_id="verify:start"))


class Verification(commands.Cog, name="verification"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.messages = MessageService(session_factory)

    async def ensure_static_embed(self) -> None:
        channel_id = get_settings().verify_channel_id
        if not channel_id:
            logger.warning("VERIFY_CHANNEL_ID not set; static verify embed disabled")
            return

        async with session_factory() as session:
            flags = SqlAlchemyBotFlagRepository(session)
            sent = await flags.get(STATIC_FLAG)
        if sent:
            return

        channel = self.bot.get_channel(int(channel_id))
        if channel is None:
            logger.warning("Verify channel %s not found", channel_id)
            return

        payload = await self.messages.get_rendered("verify.static")
        embed = build_discord_embed(payload or {"description": "Weryfikacja"})
        try:
            message = await channel.send(embed=embed, view=StaticVerifyView())
        except Exception:
            logger.exception("Failed to send static verify embed")
            return

        async with session_factory() as session:
            flags = SqlAlchemyBotFlagRepository(session)
            await flags.set(STATIC_FLAG, str(message.id))

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        if interaction.type is not discord.InteractionType.component:
            return
        custom_id = (interaction.data or {}).get("custom_id")

        if custom_id == "verify:start":
            await interaction.response.send_modal(VerifyModal(self))
            return

        if custom_id != "verify:confirm":
            return

        await interaction.response.defer()
        discord_id = str(interaction.user.id)

        roblox_id = None
        async with session_factory() as session:
            pending = await SqlAlchemyVerificationRepository(session).get_pending(discord_id)
        if pending is not None:
            roblox_id = pending.roblox_id

        async with session_factory() as session:
            use_cases = VerificationUseCases(
                SqlAlchemyVerificationRepository(session), RobloxProfileClient()
            )
            status = await use_cases.confirm(discord_id)

        key = STATUS_KEYS.get(status, "verify.start")
        payload = await self.messages.get_rendered(
            key, {"roblox_id": roblox_id or ""}
        )
        embed = build_discord_embed(payload or {"description": "Nieznany błąd."})
        await interaction.edit_original_response(embed=embed, view=None)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Verification(bot))

