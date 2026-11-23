from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.content.application.interfaces import ContentRepository
from app.modules.content.domain.entities import ContentTemplateEntity
from app.modules.content.infrastructure.models import ContentTemplate


class SqlAlchemyContentRepository(ContentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, key: str) -> ContentTemplateEntity | None:
        result = await self._session.execute(
            select(ContentTemplate).where(ContentTemplate.key == key)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return ContentTemplateEntity(key=row.key, payload=row.payload)

    async def list(self) -> list[ContentTemplateEntity]:
        result = await self._session.execute(select(ContentTemplate).order_by(ContentTemplate.key))
        rows = result.scalars().all()
        return [ContentTemplateEntity(key=row.key, payload=row.payload) for row in rows]

    async def upsert(self, key: str, payload: dict[str, Any]) -> ContentTemplateEntity:
        result = await self._session.execute(
            select(ContentTemplate).where(ContentTemplate.key == key)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = ContentTemplate(key=key, payload=payload)
            self._session.add(row)
        else:
            row.payload = payload
        await self._session.commit()
        await self._session.refresh(row)
        return ContentTemplateEntity(key=row.key, payload=row.payload)

