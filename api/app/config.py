"""Runtime settings loaded from environment / .env."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    secret_key: str = "CHANGE-ME"
    jwt_algorithm: str = "HS256"
    token_expires_minutes: int = 60
    rate_limit: str = "10/minute"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]
    slowapi_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
