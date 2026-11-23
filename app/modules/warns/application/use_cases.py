from app.modules.warns.application.interfaces import WarnRepository
from app.modules.warns.domain.entities import WarnEntity


class WarnUseCases:
    def __init__(self, repository: WarnRepository) -> None:
        self._repository = repository

    async def add(
        self, user_id: int, server_id: int, moderator_id: int, reason: str
    ) -> int:
        return await self._repository.add(user_id, server_id, moderator_id, reason)

    async def remove(self, warn_id: int, user_id: int, server_id: int) -> int:
        return await self._repository.remove(warn_id, user_id, server_id)

    async def list_for_user(
        self, user_id: int, server_id: int
    ) -> list[WarnEntity]:
        return await self._repository.list(user_id, server_id)

    async def list_all(self) -> list[WarnEntity]:
        return await self._repository.list_all()

