from typing import Any

from app.modules.strefa.application.interfaces import (
    ApplicationRepository,
    EventTemplateRepository,
    StrefaCommandRepository,
)
from app.modules.strefa.domain.entities import ApplicationEntity, StrefaCommandEntity


class StrefaUseCases:
    def __init__(
        self,
        commands: StrefaCommandRepository,
        applications: ApplicationRepository,
        events: EventTemplateRepository,
    ) -> None:
        self._commands = commands
        self._applications = applications
        self._events = events

    async def active_commands(self) -> list[StrefaCommandEntity]:
        return [c for c in await self._commands.list() if not c.deleted]

    async def applications(self) -> list[ApplicationEntity]:
        return await self._applications.list()

    async def applications_for_parent(self, parent_channel: str) -> list[ApplicationEntity]:
        return await self._applications.list_by_parent(parent_channel)

    async def application(self, application_id: int) -> ApplicationEntity | None:
        return await self._applications.get_by_id(application_id)

    async def event_template(self, key: str) -> dict[str, Any] | None:
        return await self._events.get(key)

