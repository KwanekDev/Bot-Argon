"""Gateway bridging Discord cogs to the warns application layer."""
from app.core.database import session_factory
from app.modules.warns.application.use_cases import WarnUseCases
from app.modules.warns.domain.entities import WarnEntity
from app.modules.warns.infrastructure.repositories import SqlAlchemyWarnRepository


class BotWarnGateway:
    """Per-call session gateway used by Discord cogs."""

    async def add_warn(
        self, user_id: int, server_id: int, moderator_id: int, reason: str
    ) -> int:
        async with session_factory() as session:
            use_cases = WarnUseCases(SqlAlchemyWarnRepository(session))
            return await use_cases.add(user_id, server_id, moderator_id, reason)

    async def remove_warn(
        self, warn_id: int, user_id: int, server_id: int
    ) -> int:
        async with session_factory() as session:
            use_cases = WarnUseCases(SqlAlchemyWarnRepository(session))
            return await use_cases.remove(warn_id, user_id, server_id)

    async def list_for_user(
        self, user_id: int, server_id: int
    ) -> list[WarnEntity]:
        async with session_factory() as session:
            use_cases = WarnUseCases(SqlAlchemyWarnRepository(session))
            return await use_cases.list_for_user(user_id, server_id)

