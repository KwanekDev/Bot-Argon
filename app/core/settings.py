"""Application settings loaded from environment / .env."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_title: str = "Bot Argon API"
    app_version: str = "0.2.0"
    environment: str = "development"

    secret_key: str = "CHANGE-ME"
    jwt_algorithm: str = "HS256"
    token_expires_minutes: int = 60

    rate_limit: str = "10/minute"
    slowapi_enabled: bool = True

    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    database_path: str = "database/database.db"
    verify_channel_id: str = ""
    discord_guild_id: str = ""
    admin_username: str = ""
    admin_password: str = ""
    strefa_welcome_channel: str = ""
    strefa_create_character_channel: str = ""
    strefa_create_test_channel: str = ""
    strefa_application_logs_channel: str = ""
    strefa_public_app_logs_channel: str = ""
    strefa_character_logs_channel: str = ""
    strefa_tests_logs_channel: str = ""
    strefa_boost_channel: str = ""
    strefa_accept_characters_role: str = ""
    strefa_accept_tests_role: str = ""
    strefa_supporter_role: str = ""
    strefa_dev_ids: str = ""
    strefa_ping_role: str = ""
    strefa_applications_parent_channel: str = ""
    strefa_poll_emojis: str = "👍,👎"
    strefa_warns_logs_channel: str = ""

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{Path(self.database_path).resolve()}"


@lru_cache
def get_settings() -> Settings:
    return Settings()

