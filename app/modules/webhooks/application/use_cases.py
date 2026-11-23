from app.modules.webhooks.application.interfaces import WebhookRepository
from app.modules.webhooks.domain.entities import WebhookEntity


class WebhookUseCases:
    def __init__(self, repository: WebhookRepository) -> None:
        self._repository = repository

    async def create(self, name: str, url: str, color: int = 0) -> WebhookEntity:
        return await self._repository.create(name, url, color)

    async def list(self) -> list[WebhookEntity]:
        return await self._repository.list()

    async def update_color(self, webhook_id: int, color: int) -> WebhookEntity | None:
        return await self._repository.update(webhook_id, color=color)

    async def update(self, webhook_id: int, **fields) -> WebhookEntity | None:
        return await self._repository.update(webhook_id, **fields)

    async def delete(self, webhook_id: int) -> bool:
        return await self._repository.delete(webhook_id)

