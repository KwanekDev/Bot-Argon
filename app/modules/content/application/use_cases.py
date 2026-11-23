from typing import Any

from app.modules.content.application.interfaces import ContentRepository
from app.modules.content.domain.entities import ContentTemplateEntity


class ContentUseCases:
    def __init__(self, repository: ContentRepository) -> None:
        self._repository = repository

    async def list_templates(self) -> list[ContentTemplateEntity]:
        return await self._repository.list()

    async def get_template(self, key: str) -> ContentTemplateEntity | None:
        return await self._repository.get(key)

    async def update_template(
        self, key: str, payload: dict[str, Any]
    ) -> ContentTemplateEntity:
        return await self._repository.upsert(key, payload)

