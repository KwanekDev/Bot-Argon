from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserEntity:
    id: int
    username: str
    role: str
    password_hash: str


@dataclass(frozen=True)
class ApiKeyEntity:
    id: int
    name: str
    key_hash: str
    owner_id: int
    scopes: str = "read"
    created_at: datetime | None = None

