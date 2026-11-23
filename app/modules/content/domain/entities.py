from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContentTemplateEntity:
    key: str
    payload: dict[str, Any]

