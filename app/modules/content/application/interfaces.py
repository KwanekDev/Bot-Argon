from typing import Any, Protocol

from app.modules.content.domain.entities import ContentTemplateEntity


class ContentRepository(Protocol):
    async def get(self, key: str) -> ContentTemplateEntity | None: ...

    async def list(self) -> list[ContentTemplateEntity]: ...

    async def upsert(self, key: str, payload: dict[str, Any]) -> ContentTemplateEntity: ...

