from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.webhooks.application.interfaces import WebhookRepository
from app.modules.webhooks.domain.entities import WebhookEntity
from app.modules.webhooks.infrastructure.models import Webhook


class SqlAlchemyWebhookRepository(WebhookRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, name: str, url: str, color: int = 0) -> WebhookEntity:
        row = Webhook(name=name, url=url, color=color)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return self._to_entity(row)

    async def list(self) -> list[WebhookEntity]:
        result = await self._session.execute(select(Webhook).order_by(Webhook.id))
        return [self._to_entity(r) for r in result.scalars().all()]

    async def get(self, webhook_id: int) -> WebhookEntity | None:
        result = await self._session.execute(
            select(Webhook).where(Webhook.id == webhook_id)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def get_by_name(self, name: str) -> WebhookEntity | None:
        result = await self._session.execute(
            select(Webhook).where(Webhook.name == name)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def first_enabled(self) -> WebhookEntity | None:
        result = await self._session.execute(
            select(Webhook).where(Webhook.enabled.is_(True)).order_by(Webhook.id).limit(1)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def update(self, webhook_id: int, **fields) -> WebhookEntity | None:
        result = await self._session.execute(
            select(Webhook).where(Webhook.id == webhook_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        for key, value in fields.items():
            if hasattr(row, key):
                setattr(row, key, value)
        await self._session.commit()
        await self._session.refresh(row)
        return self._to_entity(row)

    async def delete(self, webhook_id: int) -> bool:
        result = await self._session.execute(
            delete(Webhook).where(Webhook.id == webhook_id)
        )
        await self._session.commit()
        return result.rowcount > 0

    @staticmethod
    def _to_entity(row: Webhook) -> WebhookEntity:
        return WebhookEntity(id=row.id, name=row.name, url=row.url, color=row.color, enabled=row.enabled)

