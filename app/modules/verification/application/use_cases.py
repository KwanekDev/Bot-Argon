import secrets
from datetime import datetime, timedelta

from app.modules.verification.application.interfaces import (
    RobloxProfileClient,
    VerificationRepository,
)
from app.modules.verification.domain.entities import PendingVerificationEntity
from app.modules.verification.domain.enums import VerificationStatus


class VerificationUseCases:
    def __init__(self, repository: VerificationRepository, client: RobloxProfileClient) -> None:
        self._repository = repository
        self._client = client

    async def start(self, discord_id: str, roblox_id: str) -> str:
        code = secrets.token_hex(3).upper()
        pending = PendingVerificationEntity(
            discord_id=discord_id,
            code=code,
            roblox_id=roblox_id,
            expires_at=datetime.now() + timedelta(minutes=15),
        )
        await self._repository.save_pending(pending)
        return code

    async def confirm(self, discord_id: str) -> VerificationStatus:
        pending = await self._repository.get_pending(discord_id)
        if pending is None:
            return VerificationStatus.NO_PENDING
        if pending.expires_at < datetime.now():
            await self._repository.delete_pending(discord_id)
            return VerificationStatus.FAIL_EXPIRED

        if await self._repository.get_link_by_discord(discord_id) is not None:
            await self._repository.delete_pending(discord_id)
            return VerificationStatus.ALREADY_LINKED
        if await self._repository.get_link_by_roblox(pending.roblox_id) is not None:
            await self._repository.delete_pending(discord_id)
            return VerificationStatus.ALREADY_LINKED

        blurb = await self._client.fetch_blurb(pending.roblox_id)
        if blurb is None:
            await self._repository.delete_pending(discord_id)
            return VerificationStatus.FAIL_NOTFOUND
        if blurb.strip().upper() != pending.code:
            await self._repository.delete_pending(discord_id)
            return VerificationStatus.FAIL_CODE

        await self._repository.upsert_link(discord_id, pending.roblox_id)
        await self._repository.delete_pending(discord_id)
        return VerificationStatus.SUCCESS

