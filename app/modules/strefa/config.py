"""Strefa server defaults (override via env/DB in production)."""
from app.core.settings import get_settings

SETTINGS = get_settings()

GUILD_ID = SETTINGS.discord_guild_id or "1297167121318412369"

CHANNELS = {
    "welcome": SETTINGS.strefa_welcome_channel or "1297181125264932965",
    "create_character": SETTINGS.strefa_create_character_channel or "1299089004712689674",
    "create_test": SETTINGS.strefa_create_test_channel or "1317206956565336188",
    "application_logs": SETTINGS.strefa_application_logs_channel or "1307332308499566632",
    "public_app_logs": SETTINGS.strefa_public_app_logs_channel or "1299089747658145884",
    "character_logs": SETTINGS.strefa_character_logs_channel or "1307762138244452402",
    "tests_logs": SETTINGS.strefa_tests_logs_channel or "1317171522020048988",
}

ROLES = {
    "accept_characters": SETTINGS.strefa_accept_characters_role or "1297167315548246116",
    "accept_tests": SETTINGS.strefa_accept_tests_role or "1297167315548246116",
    "supporter": SETTINGS.strefa_supporter_role or "",
}

CHANNELS["warns_logs"] = SETTINGS.strefa_warns_logs_channel

ACTIVITY = "🌲 SCP Strefa Argon RolePlay"

LEADING_COLOR = 0xB4D1EE
GRAY = 0x7D7D7D
MORPH_ACCENT = 0x00AAFF
TRY_SUCCESS = 0x186E1C
TRY_FAILURE = 0x730F0B
SUCCESS_GREEN = 0x1F8B4C
FAILURE_RED = 0xB81111
TIMEOUT_YELLOW = 0xFFFF00

FOOTER_TEXT = "Strefa Argon RolePlay"
FOOTER_ICON = "https://i.postimg.cc/3xVDPgNV/obraz-2025-07-17-164958411.png"

DENY_MESSAGE = "Nie masz odpowiednich uprawnień aby użyć tą komendę."

