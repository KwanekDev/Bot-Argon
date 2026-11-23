from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.verification.application.interfaces import VerificationRepository
from app.modules.verification.domain.entities import (
    PendingVerificationEntity,
    RobloxLinkEntity,
)
from app.modules.verification.infrastructure.models import PendingVerification, RobloxLink


class SqlAlchemyVerificationRepository(VerificationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_link_by_discord(self, discord_id: str) -> RobloxLinkEntity | None:
        result = await self._session.execute(
            select(RobloxLink).where(RobloxLink.discord_id == discord_id)
        )
        row = result.scalar_one_or_none()
        return self._to_link(row) if row else None

    async def get_link_by_roblox(self, roblox_id: str) -> RobloxLinkEntity | None:
        result = await self._session.execute(
            select(RobloxLink).where(RobloxLink.roblox_id == roblox_id)
        )
        row = result.scalar_one_or_none()
        return self._to_link(row) if row else None

    async def upsert_link(self, discord_id: str, roblox_id: str) -> RobloxLinkEntity:
        result = await self._session.execute(
            select(RobloxLink).where(RobloxLink.discord_id == discord_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = RobloxLink(discord_id=discord_id, roblox_id=roblox_id)
            self._session.add(row)
        else:
            row.roblox_id = roblox_id
        await self._session.commit()
        await self._session.refresh(row)
        return self._to_link(row)

    async def save_pending(self, pending: PendingVerificationEntity) -> None:
        result = await self._session.execute(
            select(PendingVerification).where(PendingVerification.discord_id == pending.discord_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = PendingVerification(
                discord_id=pending.discord_id,
                code=pending.code,
                roblox_id=pending.roblox_id,
                expires_at=pending.expires_at,
            )
            self._session.add(row)
        else:
            row.code = pending.code
            row.roblox_id = pending.roblox_id
            row.expires_at = pending.expires_at
        await self._session.commit()

    async def get_pending(self, discord_id: str) -> PendingVerificationEntity | None:
        result = await self._session.execute(
            select(PendingVerification).where(PendingVerification.discord_id == discord_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return PendingVerificationEntity(
            discord_id=row.discord_id,
            code=row.code,
            roblox_id=row.roblox_id,
            expires_at=row.expires_at,
        )

    async def delete_pending(self, discord_id: str) -> None:
        result = await self._session.execute(
            select(PendingVerification).where(PendingVerification.discord_id == discord_id)
        )
        row = result.scalar_one_or_none()
        if row is not None:
            await self._session.delete(row)
            await self._session.commit()

    @staticmethod
    def _to_link(row: RobloxLink) -> RobloxLinkEntity:
        return RobloxLinkEntity(
            discord_id=row.discord_id, roblox_id=row.roblox_id, verified_at=row.verified_at
        )

