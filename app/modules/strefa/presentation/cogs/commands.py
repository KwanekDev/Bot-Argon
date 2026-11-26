"""Strefa Argon: statyczne slash commands (app_commands)."""
import datetime
import logging
import random

import discord
from discord import app_commands
from discord.ext import commands

from app.core.database import session_factory
from app.modules.strefa import config as C
from app.modules.strefa.infrastructure.repositories import SqlAlchemyStrefaCommandRepository
from app.modules.warns.infrastructure.repositories import SqlAlchemyWarnRepository
from app.modules.warns.infrastructure.models import Warn
from sqlalchemy import delete
from app.modules.strefa.infrastructure.roblox import roblox_username_exists
from app.modules.strefa.presentation.cogs.helpers import build_embed, send_ephemeral, send_public
from app.modules.strefa.presentation.cogs.helpers import send_channel_log
from app.modules.strefa.presentation.cogs.helpers import apply_payload, load_template

logger = logging.getLogger("bot_argon.strefa.commands")

NL = chr(10)


class StrefaCommands(commands.Cog, name="strefa_commands"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _run(self, name: str, interaction: discord.Interaction, kwargs: dict) -> None:
        await interaction.response.defer()
        async with session_factory() as session:
            repo = SqlAlchemyStrefaCommandRepository(session)
            meta = next((c for c in await repo.list(include_deleted=True) if c.name == name), None)
        if meta is None:
            return
        if meta.devonly:
            allowed = {int(x) for x in C.SETTINGS.strefa_dev_ids.split(",")} if C.SETTINGS.strefa_dev_ids else set()
            if interaction.user.id not in allowed:
                await send_ephemeral(interaction, C.DENY_MESSAGE)
                return
        if meta.testonly:
            if not C.SETTINGS.discord_guild_id or str(interaction.guild_id) != C.SETTINGS.discord_guild_id:
                await send_ephemeral(interaction, C.DENY_MESSAGE)
                return
        if meta.permissions_required:
            perms = interaction.user.guild_permissions
            if not all(getattr(perms, p, False) for p in meta.permissions_required):
                await send_ephemeral(interaction, C.DENY_MESSAGE)
                return
        if meta.bot_permissions:
            perms = interaction.guild.me.guild_permissions
            if not all(getattr(perms, p, False) for p in meta.bot_permissions):
                await send_ephemeral(interaction, C.DENY_MESSAGE)
                return
        handler = getattr(self, f"_h_{name.replace('-', '_')}", None)
        if handler is None:
            await send_ephemeral(interaction, "Ta komenda nie jest jeszcze gotowa.")
            return
        await handler(interaction, kwargs)

    # =============================================================== KOMENDY
    @app_commands.command(name="jak-zrobic-wlasne-teamy", description="jak zrobic wlasne teamy")
    async def jak_zrobic_wlasne_teamy(self, interaction: discord.Interaction) -> None:
        await self._run("jak-zrobic-wlasne-teamy", interaction, {})

    @app_commands.command(name="credits", description="Twórca bota")
    async def credits(self, interaction: discord.Interaction) -> None:
        await self._run("credits", interaction, {})

    @app_commands.command(name="try", description="Pomocnik losowości RP")
    async def try_cmd(self, interaction: discord.Interaction, szansa_na_powodzenie: int) -> None:
        await self._run("try", interaction, {"szansa_na_powodzenie": szansa_na_powodzenie})

    @app_commands.command(name="ankieta-roleplay", description="Ankieta roleplay")
    async def ankieta_roleplay(
        self,
        interaction: discord.Interaction,
        pierwsza_godzina: str,
        druga_godzina: str,
        trzecia_godzina: str | None = None,
    ) -> None:
        await self._run("ankieta-roleplay", interaction, {
            "pierwsza_godzina": pierwsza_godzina,
            "druga_godzina": druga_godzina,
            "trzecia_godzina": trzecia_godzina,
        })

    @app_commands.command(name="decyzja-roleplay", description="Decyzja roleplay")
    async def decyzja_roleplay(
        self,
        interaction: discord.Interaction,
        godzina: str,
        prowadzacy: str,
        mapa: str,
    ) -> None:
        await self._run("decyzja-roleplay", interaction, {
            "godzina": godzina, "prowadzacy": prowadzacy, "mapa": mapa,
        })

    @app_commands.command(name="kto-powinien-hostowac-sesje-rp", description="Kto hostuje sesję RP")
    async def kto_powinien_hostowac_sesje_rp(self, interaction: discord.Interaction) -> None:
        await self._run("kto-powinien-hostowac-sesje-rp", interaction, {})

    @app_commands.command(name="rozpocznij-sesje", description="Rozpocznij sesję")
    async def rozpocznij_sesje(self, interaction: discord.Interaction, prowadzacy: str) -> None:
        await self._run("rozpocznij-sesje", interaction, {"prowadzacy": prowadzacy})

    @app_commands.command(name="test-aktywnosci", description="Test aktywności")
    async def test_aktywnosci(self, interaction: discord.Interaction, opis_testu: str) -> None:
        await self._run("test-aktywnosci", interaction, {"opis_testu": opis_testu})

    @app_commands.command(name="zbanuj", description="Zbanuj gracza")
    async def zbanuj(
        self,
        interaction: discord.Interaction,
        typ: str,
        osoba: discord.User,
        powod: str,
        odwolanie: str,
    ) -> None:
        await self._run("zbanuj", interaction, {
            "typ": typ, "osoba": osoba, "powod": powod, "odwolanie": odwolanie,
        })

    @app_commands.command(name="black-lista", description="Czarna lista")
    async def black_lista(
        self,
        interaction: discord.Interaction,
        osoba: discord.User,
        powod: str,
        odwolanie: str,
    ) -> None:
        await self._run("black-lista", interaction, {
            "osoba": osoba, "powod": powod, "odwolanie": odwolanie,
        })

    @app_commands.command(name="ostrzezenie", description="Ostrzeżenie")
    async def ostrzezenie(
        self,
        interaction: discord.Interaction,
        osoba: discord.User,
        powod: str,
    ) -> None:
        await self._run("ostrzezenie", interaction, {
            "osoba": osoba, "powod": powod,
        })

    @app_commands.command(name="ostrzezenia", description="Lista ostrzeżeń")
    async def ostrzezenia(self, interaction: discord.Interaction, osoba: discord.User) -> None:
        await self._run("ostrzezenia", interaction, {"osoba": osoba})

    @app_commands.command(name="usun-ostrzezenie", description="Usuń ostrzeżenie (staff)")
    async def usun_ostrzezenie(self, interaction: discord.Interaction, id: int) -> None:
        await self._run("usun-ostrzezenie", interaction, {"id": id})

    @app_commands.command(name="wezwij", description="Wezwij gracza")
    async def wezwij(
        self,
        interaction: discord.Interaction,
        osoba: discord.User,
        czas: str,
        kanal: discord.TextChannel,
        powod: str,
    ) -> None:
        await self._run("wezwij", interaction, {
            "osoba": osoba, "czas": czas, "kanal": kanal, "powod": powod,
        })

    @app_commands.command(name="stworz-morpha", description="Morph (wspierający)")
    async def stworz_morpha(
        self,
        interaction: discord.Interaction,
        nick_roblox: str,
        id_czapek: int,
        id_koszulki: int,
        id_spodni: int,
        nazwa_morpha: str | None = None,
        noktowizja: bool | None = False,
        morph_gra: str | None = None,
    ) -> None:
        await self._run("stworz-morpha", interaction, {
            "nick_roblox": nick_roblox,
            "id_czapek": id_czapek,
            "id_koszulki": id_koszulki,
            "id_spodni": id_spodni,
            "nazwa_morpha": nazwa_morpha,
            "noktowizja": noktowizja,
            "morph_gra": morph_gra,
        })

    @app_commands.command(name="stworz-postac", description="Stwórz postać")
    async def stworz_postac(
        self,
        interaction: discord.Interaction,
        nick_roblox: str,
        imie_i_nazwisko: str,
        data_urodzenia: str,
        narodowosc: str,
        departament: str,
        opis: str,
    ) -> None:
        await self._run("stworz-postac", interaction, {
            "nick_roblox": nick_roblox,
            "imie_i_nazwisko": imie_i_nazwisko,
            "data_urodzenia": data_urodzenia,
            "narodowosc": narodowosc,
            "departament": departament,
            "opis": opis,
        })

    @app_commands.command(name="wniosek-o-badania", description="Wniosek o badania")
    async def wniosek_o_badania(
        self,
        interaction: discord.Interaction,
        nick_roblox: str,
        podmiot_scp: str,
        opis_testu: str,
        liczba_kd: int,
    ) -> None:
        await self._run("wniosek-o-badania", interaction, {
            "nick_roblox": nick_roblox,
            "podmiot_scp": podmiot_scp,
            "opis_testu": opis_testu,
            "liczba_kd": liczba_kd,
        })

    # =============================================================== HANDLERY
    async def _h_jak_zrobic_wlasne_teamy(self, interaction, kwargs) -> None:
        text = (
            "**Jak zrobić własne teamy**"
            + NL + NL
            + "* 1. Wejdź na serwer Argon RolePlay."
            + NL
            + "* 2. Przejdź na kanał <#1299089627986137108> i przeczytaj zasady."
            + NL
            + "* 3. Skontaktuj się z administracją, aby utworzyć własny team."
            + NL
            + "* 4. Poczekaj na akceptację i otrzymaj rolę."
            + NL
        )
        await interaction.followup.send(text)

    async def _h_credits(self, interaction, kwargs) -> None:
        await interaction.followup.send("Bot stworzony przez <@1307023522517745674> ⚙️")

    async def _h_try(self, interaction, kwargs) -> None:
        chance = int(kwargs.get("szansa_na_powodzenie") or 50)
        chance = max(0, min(100, chance))
        roll = random.randint(1, 100)
        success = roll <= chance
        content = f"||@{interaction.user}||"
        if success:
            embed = build_embed("UDAŁO SIĘ", "", C.TRY_SUCCESS)
        else:
            embed = build_embed("NIE UDAŁO SIĘ", "", C.TRY_FAILURE)
        embed.description = f"* Rzut: **{roll}/100** (szansa {chance}%)."
        await interaction.followup.send(content=content, embed=embed)

    async def _h_ankieta_roleplay(self, interaction, kwargs) -> None:
        fields = [("Pierwsza godzina", str(kwargs.get("pierwsza_godzina", "-"))), ("Druga godzina", str(kwargs.get("druga_godzina", "-")))]
        if kwargs.get("trzecia_godzina"):
            fields.append(("Trzecia godzina", str(kwargs["trzecia_godzina"])))
        payload = await load_template("strefa.announce_poll")
        embed = apply_payload(build_embed("ANKIETA ROLEPLAY", "", C.LEADING_COLOR), payload)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        msg = await send_public(interaction, embed, content=await _ping_content())
        await _add_poll_reactions(interaction, msg)

    async def _h_decyzja_roleplay(self, interaction, kwargs) -> None:
        fields = [
            ("Godzina", str(kwargs.get("godzina", "-"))),
            ("Prowadzący", str(kwargs.get("prowadzacy", "-"))),
            ("Mapa", str(kwargs.get("mapa", "-"))),
        ]
        payload = await load_template("strefa.announce_decision")
        embed = apply_payload(build_embed("DECYZJA ROLEPLAY", "", C.LEADING_COLOR), payload)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        msg = await send_public(interaction, embed, content=await _ping_content())
        await _add_poll_reactions(interaction, msg)

    async def _h_kto_powinien_hostowac_sesje_rp(self, interaction, kwargs) -> None:
        payload = await load_template("strefa.announce_host")
        embed = apply_payload(build_embed("HOST SESJI RP", "Sesje hostuje **Prowadzący**!", C.LEADING_COLOR), payload)
        await send_public(interaction, embed, content=await _ping_content())

    async def _h_rozpocznij_sesje(self, interaction, kwargs) -> None:
        fields = [("Prowadzący", str(kwargs.get("prowadzacy", "-"))), ("Link do gry", "https://www.roblox.com/games/start?placeId=0")]
        payload = await load_template("strefa.announce_start")
        embed = apply_payload(build_embed("ROZPOCZNIJ SESJĘ", "Sesja właśnie się rozpoczyna!", C.LEADING_COLOR), payload)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        await send_public(interaction, embed, content=await _ping_content())

    async def _h_test_aktywnosci(self, interaction, kwargs) -> None:
        desc = kwargs.get("opis_testu", "Test aktywności")
        payload = await load_template("strefa.announce_activity")
        embed = apply_payload(build_embed("TEST AKTYWNOŚCI", str(desc), C.LEADING_COLOR), payload)
        msg = await send_public(interaction, embed, content=await _ping_content())
        await _add_poll_reactions(interaction, msg)

    async def _h_zbanuj(self, interaction, kwargs) -> None:
        await self._punish(interaction, kwargs, "ZBANOWANIA", "ZOSTAŁEŚ ZBANOWANY NA SERWERZE!")

    async def _h_black_lista(self, interaction, kwargs) -> None:
        await self._punish(interaction, kwargs, "CZARNA LISTA", "ZOSTAŁEŚ DODANY NA CZARNĄ LISTĘ!")

    async def _h_ostrzezenie(self, interaction, kwargs) -> None:
        await self._warn(interaction, kwargs)

    async def _punish(self, interaction, kwargs, title: str, dm_title: str) -> None:
        target = kwargs.get("osoba")
        reason = str(kwargs.get("powod", "-"))
        fields = [
            ("Administrator", str(interaction.user)),
            ("Powód", reason),
            ("Data", datetime.datetime.now().strftime("%d/%m/%Y %H:%M")),
        ]
        payload = await load_template("strefa.punish_public", {"title": title})
        embed = apply_payload(build_embed(title, "", C.LEADING_COLOR), payload)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        if not interaction.user.guild_permissions.ban_members:
            await send_ephemeral(interaction, C.DENY_MESSAGE)
            return
        if not interaction.guild.me.guild_permissions.ban_members:
            await send_ephemeral(interaction, "Bot nie ma uprawnień do banowania.")
            return
        if isinstance(target, discord.User):
            try:
                await interaction.guild.ban(target, reason=f"{title}: {reason}")
            except discord.Forbidden:
                await send_ephemeral(interaction, "Brak uprawnień bota do zbanowania tej osoby.")
                return
            except Exception:
                await send_ephemeral(interaction, "Nie udało się zbanować tej osoby.")
                return
        await send_public(interaction, embed)
        await send_channel_log(interaction.client, "application_logs", title, f"Użytkownik: <@{target.id}> | Moderator: {interaction.user}")

        if target is not None and isinstance(target, discord.User):
            dm_payload = await load_template("strefa.punish_dm", {"title": dm_title, "reason": reason})
            dm = apply_payload(build_embed(dm_title, "", C.FAILURE_RED), dm_payload)
            if dm.description is None:
                dm.description = f"Powód: {reason}" + NL + NL + "* Jeśli uważasz, że to pomyłka, złóż odwołanie do administracji."
            try:
                await target.send(embed=dm)
            except Exception:
                pass

    async def _warn(self, interaction, kwargs) -> None:
        if not interaction.user.guild_permissions.manage_messages:
            await send_ephemeral(interaction, C.DENY_MESSAGE)
            return
        target = kwargs.get("osoba")
        reason = str(kwargs.get("powod", "-"))
        async with session_factory() as session:
            repo = SqlAlchemyWarnRepository(session)
            warn_id = await repo.add(target.id, interaction.guild_id, interaction.user.id, reason)
            total = await repo.count(target.id, interaction.guild_id)
        fields = [
            ("Numer", str(warn_id)),
            ("Powód", reason),
            ("Moderator", str(interaction.user)),
            ("Łącznie ostrzeżeń", str(total)),
        ]
        payload = await load_template("strefa.punish_public", {"title": "OSTRZEŻENIA"})
        embed = apply_payload(build_embed("OSTRZEŻENIA", "", C.LEADING_COLOR), payload)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        await send_public(interaction, embed)
        if isinstance(target, discord.User):
            dm = build_embed("ZOSTAŁEŚ OSTRZEŻONY!", f"Powód: {reason}" + NL + NL + "* Jeśli uważasz, że to pomyłka, złóż odwołanie.", C.FAILURE_RED)
            try:
                await target.send(embed=dm)
            except Exception:
                pass
        await send_channel_log(interaction.client, "warns_logs", "LOG OSTRZEŻENIA", f"Użytkownik: <@{target.id}> | Moderator: {interaction.user}")

    async def _h_ostrzezenia(self, interaction, kwargs) -> None:
        target = kwargs.get("osoba")
        if target.id != interaction.user.id and not interaction.user.guild_permissions.manage_messages:
            await send_ephemeral(interaction, C.DENY_MESSAGE)
            return
        async with session_factory() as session:
            warns = await SqlAlchemyWarnRepository(session).list(target.id, interaction.guild_id)
        embed = build_embed("OSTRZEŻENIA", f"Użytkownik: <@{target.id}>", C.LEADING_COLOR)
        if not warns:
            embed.description += NL + "* Brak ostrzeżeń."
        for w in warns:
            embed.add_field(name=f"#{w.id}", value=f"Powód: {w.reason}" + NL + f"Data: {w.created_at}" + NL + f"Moderator: <@{w.moderator_id}>", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def _h_usun_ostrzezenie(self, interaction, kwargs) -> None:
        if not interaction.user.guild_permissions.manage_messages:
            await send_ephemeral(interaction, C.DENY_MESSAGE)
            return
        warn_id = int(kwargs.get("id"))
        async with session_factory() as session:
            await session.execute(delete(Warn).where(Warn.id == warn_id, Warn.server_id == str(interaction.guild_id)))
            await session.commit()
        await interaction.followup.send(f"Usunięto ostrzeżenie #{warn_id}.", ephemeral=True)

    async def _h_wezwij(self, interaction, kwargs) -> None:
        target = kwargs.get("osoba")
        fields = [
            ("Czas", str(kwargs.get("czas", "-"))),
            ("Kanał", str(kwargs.get("kanal", "-"))),
            ("Powód", str(kwargs.get("powod", "-"))),
        ]
        payload = await load_template("strefa.summon")
        embed = apply_payload(build_embed("WEZWANIE", "", C.LEADING_COLOR), payload)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        content = f"||@{target}||" if isinstance(target, discord.User) else None
        await send_public(interaction, embed, content=content)

    async def _h_stworz_morpha(self, interaction, kwargs) -> None:
        if C.ROLES["supporter"]:
            allowed = [r.id for r in interaction.user.roles]
            if int(C.ROLES["supporter"]) not in allowed:
                await send_ephemeral(interaction, "Jedynie dla wspierających!")
                return
        fields = [
            ("Nick Roblox", str(kwargs.get("nick_roblox", "-"))),
            ("ID czapek", str(kwargs.get("id_czapek", "-"))),
            ("ID koszulki", str(kwargs.get("id_koszulki", "-"))),
            ("ID spodni", str(kwargs.get("id_spodni", "-"))),
            ("Nazwa morpha", str(kwargs.get("nazwa_morpha", "-"))),
            ("Noktowizja", str(kwargs.get("noktowizja", False))),
            ("Morph gra", str(kwargs.get("morph_gra", "-"))),
        ]
        payload = await load_template("strefa.morph")
        embed = apply_payload(build_embed("STWÓRZ MORPHA", "", C.MORPH_ACCENT), payload)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        await interaction.followup.send(embed=embed)

    async def _h_stworz_postac(self, interaction, kwargs) -> None:
        if interaction.channel.id != int(C.CHANNELS["create_character"]):
            await send_ephemeral(interaction, f"Ta komenda może być użyta tylko na kanale <#{C.CHANNELS['create_character']}>.")
            return
        birth = str(kwargs.get("data_urodzenia", ""))
        if not _valid_date(birth):
            await send_ephemeral(interaction, "Data urodzenia musi być w formacie DD/MM/YYYY.")
            return
        nat = str(kwargs.get("narodowosc", ""))
        if len(nat) != 2 or not nat.isalpha():
            await send_ephemeral(interaction, "Narodowość musi być dwuliterowym kodem (np. PL, US).")
            return
        nick = str(kwargs.get("nick_roblox", ""))
        if not await roblox_username_exists(nick):
            await send_ephemeral(interaction, "Nie znaleziono użytkownika Roblox o podanym nicku.")
            return
        fields = [
            ("Nick Roblox", nick),
            ("Imię i nazwisko", str(kwargs.get("imie_i_nazwisko", "-"))),
            ("Data urodzenia", birth),
            ("Narodowość", nat.upper()),
            ("Departament", str(kwargs.get("departament", "-"))),
            ("Opis", str(kwargs.get("opis", "-"))),
        ]
        payload = await load_template("strefa.character_submission")
        embed = apply_payload(build_embed("WNIOSEK O POSTAĆ", f"Od użytkownika: <@{interaction.user.id}>", C.GRAY), payload)
        embed.insert_field_at(0, name=f"• <@{interaction.user.id}>", value=chr(160), inline=False)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        from app.modules.strefa.presentation.cogs.approvals import ApprovalView
        await interaction.followup.send(embed=embed, view=ApprovalView("character"))

    async def _h_wniosek_o_badania(self, interaction, kwargs) -> None:
        if interaction.channel.id != int(C.CHANNELS["create_test"]):
            await send_ephemeral(interaction, f"Ta komenda może być użyta tylko na kanale <#{C.CHANNELS['create_test']}>.")
            return
        fields = [
            ("Nick Roblox", str(kwargs.get("nick_roblox", "-"))),
            ("Podmiot SCP", str(kwargs.get("podmiot_scp", "-"))),
            ("Opis testu", str(kwargs.get("opis_testu", "-"))),
            ("Liczba KD", str(kwargs.get("liczba_kd", "-"))),
        ]
        payload = await load_template("strefa.test_submission")
        embed = apply_payload(build_embed("WNIOSEK O BADANIA", f"Od użytkownika: <@{interaction.user.id}>", C.GRAY), payload)
        embed.insert_field_at(0, name=f"• <@{interaction.user.id}>", value=chr(160), inline=False)
        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        from app.modules.strefa.presentation.cogs.approvals import ApprovalView
        await interaction.followup.send(embed=embed, view=ApprovalView("test"))


def _valid_date(value: str) -> bool:
    try:
        datetime.datetime.strptime(value, "%d/%m/%Y")
        return True
    except ValueError:
        return False


async def _ping_content() -> str | None:
    role_id = C.SETTINGS.strefa_ping_role
    if role_id:
        return f"||<@&{role_id}>||"
    return None


async def _add_poll_reactions(interaction, msg) -> None:
    if msg is None:
        return
    emojis = [e.strip() for e in C.SETTINGS.strefa_poll_emojis.split(",") if e.strip()]
    for emoji in emojis:
        try:
            await msg.add_reaction(emoji)
        except Exception:
            pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StrefaCommands(bot))

