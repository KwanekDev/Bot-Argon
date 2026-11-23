from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.discord_bot.infrastructure.models import BotFlag


class SqlAlchemyBotFlagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, flag: str) -> str | None:
        result = await self._session.execute(
            select(BotFlag).where(BotFlag.flag == flag)
        )
        row = result.scalar_one_or_none()
        return row.value if row is not None else None

    async def set(self, flag: str, value: str) -> None:
        result = await self._session.execute(
            select(BotFlag).where(BotFlag.flag == flag)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = BotFlag(flag=flag, value=value)
            self._session.add(row)
        else:
            row.value = value
        await self._session.commit()

