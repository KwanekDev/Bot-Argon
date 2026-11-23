from dataclasses import dataclass


@dataclass(frozen=True)
class WebhookEntity:
    id: int
    name: str
    url: str
    color: int = 0
    enabled: bool = True

