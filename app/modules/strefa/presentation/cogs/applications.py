"""Application engine: menus, DM flow, decisions."""
import logging

import discord
from discord.ext import commands
from discord.ui import Button, Select, View

from app.core.database import session_factory
from app.modules.strefa import config as C
from app.modules.strefa.infrastructure.repositories import SqlAlchemyApplicationRepository
from app.modules.discord_bot.infrastructure.flags import SqlAlchemyBotFlagRepository
from app.modules.strefa.presentation.cogs.helpers import build_embed
from app.modules.strefa.presentation.cogs.helpers import apply_payload, load_template

logger = logging.getLogger("bot_argon.strefa.applications")

TIMEOUT_START = 60
TIMEOUT_QUESTION = 3600  # 1h

NL = chr(10)


class ApplicationStartView(View):
    def __init__(self, application_id: int) -> None:
        super().__init__(timeout=TIMEOUT_START)
        self.application_id = application_id
        self.add_item(Button(label="Potwierdź", style=discord.ButtonStyle.success, custom_id=f"app:confirm:{application_id}"))
        self.add_item(Button(label="Anuluj", style=discord.ButtonStyle.danger, custom_id=f"app:cancel:{application_id}"))


class QuestionView(View):
    def __init__(self, application_id: int, question_index: int, options: list) -> None:
        super().__init__(timeout=TIMEOUT_QUESTION)
        for i, opt in enumerate(options):
            self.add_item(Button(label=opt.get("label", opt.get("value", str(i))), style=discord.ButtonStyle.primary, custom_id=f"app:ans:{application_id}:{question_index}:{i}"))


class DecisionView(View):
    def __init__(self, application_id: int) -> None:
        super().__init__(timeout=None)
        self.application_id = application_id
        self.add_item(Button(label="Zatwierdź", style=discord.ButtonStyle.success, custom_id=f"app:approve:{application_id}"))
        self.add_item(Button(label="Odrzuć", style=discord.ButtonStyle.danger, custom_id=f"app:decline:{application_id}"))


class Applications(commands.Cog, name="strefa_applications"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._flows = {}

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.ensure_menus()

    async def ensure_menus(self) -> None:
        async with session_factory() as session:
            apps = await SqlAlchemyApplicationRepository(session).list()
        parents = {}
        for app in apps:
            parent_id = C.SETTINGS.strefa_applications_parent_channel or app.parent_channel
            parents.setdefault(parent_id, []).append(app)
        for parent_id, apps_list in parents.items():
            channel = self.bot.get_channel(int(parent_id))
            if channel is None:
                logger.warning("Application parent channel %s not found", parent_id)
                continue
            flag_key = f"app_menu_sent_{parent_id}"
            async with session_factory() as session:
                flags = SqlAlchemyBotFlagRepository(session)
                sent = await flags.get(flag_key)
            if sent:
                continue
            payload = await load_template("strefa.app_menu")
            embed = apply_payload(build_embed("PODANIA", "", C.LEADING_COLOR), payload)
            view = View(timeout=None)
            select = Select(
                placeholder="Wybierz podanie",
                options=[
                    discord.SelectOption(label=a.name[:100], value=str(a.id)) for a in apps_list
                ],
            )
            select.custom_id = f"app:menu:{parent_id}"
            view.add_item(select)
            try:
                await channel.send(embed=embed, view=view)
                async with session_factory() as session:
                    await SqlAlchemyBotFlagRepository(session).set(flag_key, "1")
            except Exception:
                logger.exception("Failed to send application menu")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        if interaction.type is discord.InteractionType.component:
            custom_id = (interaction.data or {}).get("custom_id", "")
            if custom_id.startswith("app:menu:"):
                await self._handle_menu(interaction, custom_id)
            elif custom_id.startswith("app:confirm:"):
                await self._handle_start(interaction, custom_id, confirmed=True)
            elif custom_id.startswith("app:cancel:"):
                await self._handle_start(interaction, custom_id, confirmed=False)
            elif custom_id.startswith("app:ans:"):
                await self._handle_answer(interaction, custom_id)
            elif custom_id.startswith("app:approve:"):
                await self._handle_decision(interaction, custom_id, approve=True)
            elif custom_id.startswith("app:decline:"):
                await self._handle_decision(interaction, custom_id, approve=False)

    async def _handle_menu(self, interaction, custom_id: str) -> None:
        app_id = int(interaction.data["values"][0])
        async with session_factory() as session:
            app = await SqlAlchemyApplicationRepository(session).get_by_id(app_id)
        if app is None:
            await interaction.response.send_message("Nie znaleziono podania.", ephemeral=True)
            return
        dm_view = ApplicationStartView(app.id)
        payload = await load_template("strefa.app_start", {"name": app.name})
        embed = apply_payload(build_embed(f"Aplikacja: {app.name}", "", C.LEADING_COLOR), payload)
        try:
            await interaction.user.send(embed=embed, view=dm_view)
            await interaction.response.send_message("Sprawdź prywatną wiadomość!", ephemeral=True)
        except Exception:
            await interaction.response.send_message(embed=embed, view=dm_view, ephemeral=True)

    async def _handle_start(self, interaction, custom_id: str, confirmed: bool) -> None:
        app_id = int(custom_id.split(":")[2])
        if not confirmed:
            await interaction.message.delete()
            return
        async with session_factory() as session:
            app = await SqlAlchemyApplicationRepository(session).get_by_id(app_id)
        if app is None:
            return
        self._flows[str(interaction.user.id)] = {
            "app_id": app.id,
            "questions": app.questions,
            "index": 0,
            "answers": [],
            "message": interaction.message,
        }
        await self._ask_next(interaction)

    async def _ask_next(self, interaction: discord.Interaction) -> None:
        flow = self._flows.get(str(interaction.user.id))
        if not flow:
            return
        idx = flow["index"]
        total = len(flow["questions"])
        if idx >= total:
            await self._complete(interaction)
            return
        q = flow["questions"][idx]
        q_payload = await load_template("strefa.app_question", {"n": idx + 1, "total": total, "question": q.get("name", "")})
        embed = apply_payload(build_embed(f"Pytanie #{idx + 1}/{total}", q.get("name", ""), C.LEADING_COLOR), q_payload)
        embed.set_footer(text="Pytanie otwarte!" if q.get("type") == "Open" else "")
        if q.get("type") == "Button":
            view = QuestionView(flow["app_id"], idx, q.get("options", []))
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.edit_message(embed=embed, view=None)
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author.id == interaction.user.id and m.channel.id == interaction.channel.id,
                    timeout=TIMEOUT_QUESTION,
                )
            except Exception:
                await self._timeout(interaction)
                return
            flow["answers"].append(("Open", msg.content))
            flow["index"] += 1
            await self._ask_next(interaction)

    async def _handle_answer(self, interaction, custom_id: str) -> None:
        parts = custom_id.split(":")
        app_id = int(parts[2]); qi = int(parts[3]); oi = int(parts[4])
        flow = self._flows.get(str(interaction.user.id))
        if not flow or flow["app_id"] != app_id or flow["index"] != qi:
            return
        q = flow["questions"][qi]
        label = q["options"][oi].get("label", str(oi))
        flow["answers"].append(("Button", label))
        flow["index"] += 1
        await self._ask_next(interaction)

    async def _timeout(self, interaction) -> None:
        flow = self._flows.pop(str(interaction.user.id), None)
        if flow:
            embed = build_embed("PRZERWANO", "Za długo trwała odpowiedź.", C.TIMEOUT_YELLOW)
            try:
                await interaction.channel.send(embed=embed)
            except Exception:
                pass

    async def _complete(self, interaction) -> None:
        flow = self._flows.pop(str(interaction.user.id))
        async with session_factory() as session:
            app = await SqlAlchemyApplicationRepository(session).get_by_id(flow["app_id"])
        if app is None:
            return
        thanks_payload = await load_template("strefa.app_thanks")
        thanks = apply_payload(build_embed("DZIĘKUJEMY!", "Twoja aplikacja została wysłana do administracji.", C.SUCCESS_GREEN), thanks_payload)
        try:
            await interaction.channel.send(embed=thanks)
        except Exception:
            pass

        result_payload = await load_template("strefa.app_result", {"name": app.name})
        embed = apply_payload(build_embed(app.name, f"Od użytkownika: <@{interaction.user.id}>", C.LEADING_COLOR), result_payload)
        for i, (qtype, answer) in enumerate(flow["answers"], start=1):
            embed.add_field(name=f"Pytanie #{i}", value=str(answer), inline=False)
        channel = self.bot.get_channel(int(app.send_to))
        if channel is None:
            logger.warning("sendTo channel %s not found", app.send_to)
            return
        view = DecisionView(app.id)
        result_msg = await channel.send(embed=embed, view=view)
        self._flows[str(interaction.user.id) + "_result"] = {
            "message_id": result_msg.id,
            "applicant": interaction.user.id,
            "app_id": app.id,
        }

    async def _handle_decision(self, interaction, custom_id: str, approve: bool) -> None:
        app_id = int(custom_id.split(":")[2])
        async with session_factory() as session:
            app = await SqlAlchemyApplicationRepository(session).get_by_id(app_id)
        if app is None:
            return
        allowed = {int(r) for r in app.whitelisted_roles}
        if not allowed or not (allowed & {r.id for r in interaction.user.roles}):
            await interaction.response.send_message(C.DENY_MESSAGE, ephemeral=True)
            return
        embed = interaction.message.embeds[0] if interaction.message.embeds else None
        if embed is None:
            return
        applicant_id = _extract_applicant(embed.description or "")
        if applicant_id is None:
            await interaction.response.send_message("Nie odnaleziono autora podania.", ephemeral=True)
            return

        if approve:
            member = interaction.guild.get_member(applicant_id)
            if member is not None and app.roles_to_give:
                roles = [interaction.guild.get_role(int(r)) for r in app.roles_to_give]
                await member.add_roles(*[r for r in roles if r is not None])
            embed.color = C.SUCCESS_GREEN
            embed.set_footer(text=f"Zaakceptowane przez: {interaction.user}", icon_url=C.FOOTER_ICON)
            dm_title = "Twoja aplikacja została zaakceptowana!"
            feed = f"✅ ・ <@{applicant_id}> właśnie zdał/a aplikację {app.name}"
        else:
            embed.color = C.FAILURE_RED
            embed.set_footer(text=f"Odrzucone przez: {interaction.user}", icon_url=C.FOOTER_ICON)
            dm_title = "Twoja aplikacja została odrzucona."
            feed = f"❌  ・ <@{applicant_id}> nie zdał/a aplikacji {app.name}"

        await interaction.message.edit(embed=embed, view=None)

        try:
            user = await self.bot.fetch_user(applicant_id)
            dm_payload = await load_template("strefa.app_decision_dm", {"text": dm_title})
            dm = apply_payload(build_embed("WYNIK PODANIA", dm_title + (NL + NL + "* Jeśli uważasz, że to pomyłka, złóż odwołanie." if not approve else ""), C.SUCCESS_GREEN if approve else C.FAILURE_RED), dm_payload)
            await user.send(embed=dm)
        except Exception:
            pass

        log_channel = self.bot.get_channel(int(C.CHANNELS["application_logs"]))
        if log_channel is not None:
            log_payload = await load_template("strefa.app_log")
            log = apply_payload(build_embed("LOG PODANIA", f"[Kliknij tutaj]({interaction.message.jump_url})", C.LEADING_COLOR), log_payload)
            await log_channel.send(embed=log)
        feed_channel = self.bot.get_channel(int(C.CHANNELS["public_app_logs"]))
        if feed_channel is not None:
            await feed_channel.send(feed)


def _extract_applicant(description: str) -> int | None:
    if "Od użytkownika: <@" not in description:
        return None
    try:
        return int(description.split("Od użytkownika: <@", 1)[1].split(">", 1)[0])
    except Exception:
        return None



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Applications(bot))
