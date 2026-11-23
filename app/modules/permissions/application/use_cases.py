from app.modules.permissions.application.interfaces import CommandPermissionRepository
from app.modules.permissions.domain.entities import CommandPermissionEntity


class PermissionUseCases:
    def __init__(self, repository: CommandPermissionRepository) -> None:
        self._repository = repository

    async def get(self, command: str) -> CommandPermissionEntity | None:
        return await self._repository.get(command)

    async def list(self) -> list[CommandPermissionEntity]:
        return await self._repository.list()

    async def set(
        self, command: str, roles: list[str], permissions: list[str]
    ) -> CommandPermissionEntity:
        return await self._repository.upsert(command, roles, permissions)

