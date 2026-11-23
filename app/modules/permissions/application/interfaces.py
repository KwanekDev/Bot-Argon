from typing import Protocol

from app.modules.permissions.domain.entities import CommandPermissionEntity


class CommandPermissionRepository(Protocol):
    async def get(self, command: str) -> CommandPermissionEntity | None: ...

    async def list(self) -> list[CommandPermissionEntity]: ...

    async def upsert(
        self, command: str, roles: list[str], permissions: list[str]
    ) -> CommandPermissionEntity: ...

