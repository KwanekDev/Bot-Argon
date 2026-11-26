from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.strefa.application.interfaces import (
    ApplicationRepository,
    EventTemplateRepository,
    StrefaCommandRepository,
)
from app.modules.strefa.domain.entities import ApplicationEntity, StrefaCommandEntity
from app.modules.strefa.infrastructure.models import Application, EventTemplate, StrefaCommand


class SqlAlchemyStrefaCommandRepository(StrefaCommandRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self, include_deleted: bool = False) -> list[StrefaCommandEntity]:
        stmt = select(StrefaCommand)
        if not include_deleted:
            stmt = stmt.where(StrefaCommand.deleted.is_(False))
        result = await self._session.execute(stmt.order_by(StrefaCommand.name))
        return [self._to_entity(r) for r in result.scalars().all()]

    async def upsert(self, entity: StrefaCommandEntity) -> None:
        result = await self._session.execute(
            select(StrefaCommand).where(StrefaCommand.name == entity.name)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = StrefaCommand(name=entity.name)
            self._session.add(row)
        row.description = entity.description
        row.options = entity.options
        row.devonly = entity.devonly
        row.testonly = entity.testonly
        row.permissions_required = entity.permissions_required
        row.bot_permissions = entity.bot_permissions
        row.deleted = entity.deleted
        await self._session.commit()

    @staticmethod
    def _to_entity(row: StrefaCommand) -> StrefaCommandEntity:
        return StrefaCommandEntity(
            name=row.name,
            description=row.description,
            options=row.options or [],
            devonly=row.devonly,
            testonly=row.testonly,
            permissions_required=row.permissions_required or [],
            bot_permissions=row.bot_permissions or [],
            deleted=row.deleted,
        )


class SqlAlchemyApplicationRepository(ApplicationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self) -> list[ApplicationEntity]:
        result = await self._session.execute(select(Application).order_by(Application.id))
        return [self._to_entity(r) for r in result.scalars().all()]

    async def get_by_id(self, application_id: int) -> ApplicationEntity | None:
        result = await self._session.execute(
            select(Application).where(Application.id == application_id)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def upsert(self, entity: ApplicationEntity) -> ApplicationEntity:
        row = Application(
            name=entity.name,
            parent_channel=entity.parent_channel,
            send_to=entity.send_to,
            whitelisted_roles=entity.whitelisted_roles,
            roles_to_give=entity.roles_to_give,
            questions=entity.questions,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return self._to_entity(row)

    async def list_by_parent(self, parent_channel: str) -> list[ApplicationEntity]:
        result = await self._session.execute(
            select(Application).where(Application.parent_channel == parent_channel).order_by(Application.id)
        )
        return [self._to_entity(r) for r in result.scalars().all()]

    @staticmethod
    def _to_entity(row: Application) -> ApplicationEntity:
        return ApplicationEntity(
            id=row.id,
            name=row.name,
            parent_channel=row.parent_channel,
            send_to=row.send_to,
            whitelisted_roles=row.whitelisted_roles or [],
            roles_to_give=row.roles_to_give or [],
            questions=row.questions or [],
        )


class SqlAlchemyEventTemplateRepository(EventTemplateRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, key: str) -> dict[str, Any] | None:
        result = await self._session.execute(
            select(EventTemplate).where(EventTemplate.key == key)
        )
        row = result.scalar_one_or_none()
        return row.payload if row else None

    async def list(self) -> dict[str, dict[str, Any]]:
        result = await self._session.execute(select(EventTemplate))
        return {r.key: r.payload for r in result.scalars().all()}

    async def upsert(self, key: str, payload: dict[str, Any]) -> None:
        result = await self._session.execute(
            select(EventTemplate).where(EventTemplate.key == key)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = EventTemplate(key=key, payload=payload)
            self._session.add(row)
        else:
            row.payload = payload
        await self._session.commit()

