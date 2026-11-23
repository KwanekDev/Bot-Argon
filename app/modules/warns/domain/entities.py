from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class WarnEntity:
    id: int
    user_id: str
    server_id: str
    moderator_id: str
    reason: str
    created_at: datetime | None = None

