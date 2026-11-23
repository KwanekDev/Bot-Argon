from typing import Protocol

from app.modules.warns.domain.entities import WarnEntity


class WarnGateway(Protocol):
    async def add_warn(
        self, user_id: int, server_id: int, moderator_id: int, reason: str
    ) -> int: ...

    async def remove_warn(
        self, warn_id: int, user_id: int, server_id: int
    ) -> int: ...

    async def list_for_user(
        self, user_id: int, server_id: int
    ) -> list[WarnEntity]: ...

