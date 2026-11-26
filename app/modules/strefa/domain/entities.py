from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StrefaCommandEntity:
    name: str
    description: str = ""
    options: list[dict[str, Any]] = field(default_factory=list)
    devonly: bool = False
    testonly: bool = False
    permissions_required: list[str] = field(default_factory=list)
    bot_permissions: list[str] = field(default_factory=list)
    deleted: bool = False


@dataclass(frozen=True)
class ApplicationEntity:
    id: int | None = None
    name: str = ""
    parent_channel: str = ""
    send_to: str = ""
    whitelisted_roles: list[str] = field(default_factory=list)
    roles_to_give: list[str] = field(default_factory=list)
    questions: list[dict[str, Any]] = field(default_factory=list)

