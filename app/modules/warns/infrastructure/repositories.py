from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.warns.application.interfaces import WarnRepository
from app.modules.warns.domain.entities import WarnEntity
from app.modules.warns.infrastructure.models import Warn


class SqlAlchemyWarnRepository(WarnRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self, user_id: int, server_id: int, moderator_id: int, reason: str
    ) -> int:
        result = await self._session.execute(
            select(func.max(Warn.id)).where(
                Warn.user_id == str(user_id), Warn.server_id == str(server_id)
            )
        )
        next_id = int(result.scalar() or 0) + 1
        warn = Warn(
            id=next_id,
            user_id=str(user_id),
            server_id=str(server_id),
            moderator_id=str(moderator_id),
            reason=reason,
        )
        self._session.add(warn)
        await self._session.commit()
        return next_id

    async def remove(self, warn_id: int, user_id: int, server_id: int) -> int:
        await self._session.execute(
            delete(Warn).where(
                Warn.id == warn_id,
                Warn.user_id == str(user_id),
                Warn.server_id == str(server_id),
            )
        )
        await self._session.commit()
        return await self.count(user_id, server_id)

    async def list(
        self, user_id: int, server_id: int, limit: int = 100, offset: int = 0
    ) -> list[WarnEntity]:
        result = await self._session.execute(
            select(Warn)
            .where(Warn.user_id == str(user_id), Warn.server_id == str(server_id))
            .order_by(Warn.id.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def list_all(
        self, limit: int = 100, offset: int = 0
    ) -> list[WarnEntity]:
        result = await self._session.execute(
            select(Warn).order_by(Warn.id.desc()).limit(limit).offset(offset)
        )
        rows = result.scalars().all()
        return [self._to_entity(row) for row in rows]

    async def count(self, user_id: int, server_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Warn).where(
                Warn.user_id == str(user_id), Warn.server_id == str(server_id)
            )
        )
        return int(result.scalar() or 0)

    @staticmethod
    def _to_entity(row: Warn) -> WarnEntity:
        return WarnEntity(
            id=row.id,
            user_id=row.user_id,
            server_id=row.server_id,
            moderator_id=row.moderator_id,
            reason=row.reason,
            created_at=row.created_at,
        )

