from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RobloxLinkEntity:
    discord_id: str
    roblox_id: str
    verified_at: datetime | None = None


@dataclass(frozen=True)
class PendingVerificationEntity:
    discord_id: str
    code: str
    roblox_id: str
    expires_at: datetime

