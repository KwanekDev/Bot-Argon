from typing import Protocol

from app.modules.warns.domain.entities import WarnEntity


class WarnRepository(Protocol):
    async def add(
        self, user_id: int, server_id: int, moderator_id: int, reason: str
    ) -> int: ...

    async def remove(self, warn_id: int, user_id: int, server_id: int) -> int: ...

    async def list(
        self, user_id: int, server_id: int, limit: int = 100, offset: int = 0
    ) -> list[WarnEntity]: ...

    async def list_all(
        self, limit: int = 100, offset: int = 0
    ) -> list[WarnEntity]: ...

    async def count(self, user_id: int, server_id: int) -> int: ...

