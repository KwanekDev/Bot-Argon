"""Roblox verification cog."""
import discord
from discord import app_commands
from discord.ext import commands

from app.core.database import session_factory
from app.modules.verification.application.use_cases import VerificationUseCases
from app.modules.verification.domain.enums import VerificationStatus
from app.modules.verification.infrastructure.roblox_client import RobloxProfileClient
from app.modules.verification.infrastructure.repositories import SqlAlchemyVerificationRepository
from app.modules.webhooks.application.message_service import MessageService, build_discord_embed

STATUS_KEYS = {
    VerificationStatus.SUCCESS: "verify.success",
    VerificationStatus.FAIL_CODE: "verify.fail_code",
    VerificationStatus.FAIL_NOTFOUND: "verify.fail_notfound",
    VerificationStatus.FAIL_EXPIRED: "verify.fail_expired",
    VerificationStatus.ALREADY_LINKED: "verify.already_linked",
    VerificationStatus.NO_PENDING: "verify.start",
}


class Verification(commands.Cog, name="verification"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.messages = MessageService(session_factory)

    @commands.hybrid_command(name="verify", description="Powiąż swoje konto z Robloxem.")
    @app_commands.describe(user_id="Twój ID na Robloxie")
    async def verify(self, context: commands.Context, user_id: str) -> None:
        discord_id = str(context.author.id)
        async with session_factory() as session:
            repo = SqlAlchemyVerificationRepository(session)
            existing = await repo.get_link_by_discord(discord_id)
        if existing is not None:
            await self.messages.send_event("verify.already_linked", channel=context.channel)
            return

        async with session_factory() as session:
            repo = SqlAlchemyVerificationRepository(session)
            use_cases = VerificationUseCases(repo, RobloxProfileClient())
            code = await use_cases.start(discord_id, user_id)
        await self.messages.send_event(
            "verify.start", {"code": code, "roblox_id": user_id}, channel=context.channel
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        if interaction.type is not discord.InteractionType.component:
            return
        if (interaction.data or {}).get("custom_id") != "verify:confirm":
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

