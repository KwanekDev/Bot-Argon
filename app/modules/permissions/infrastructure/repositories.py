from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.permissions.application.interfaces import CommandPermissionRepository
from app.modules.permissions.domain.entities import CommandPermissionEntity
from app.modules.permissions.infrastructure.models import CommandPermission


class SqlAlchemyCommandPermissionRepository(CommandPermissionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, command: str) -> CommandPermissionEntity | None:
        result = await self._session.execute(
            select(CommandPermission).where(CommandPermission.command == command)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return CommandPermissionEntity(command=row.command, roles=row.roles or [], permissions=row.permissions or [])

    async def list(self) -> list[CommandPermissionEntity]:
        result = await self._session.execute(select(CommandPermission).order_by(CommandPermission.command))
        rows = result.scalars().all()
        return [
            CommandPermissionEntity(command=r.command, roles=r.roles or [], permissions=r.permissions or [])
            for r in rows
        ]

    async def upsert(
        self, command: str, roles: list[str], permissions: list[str]
    ) -> CommandPermissionEntity:
        result = await self._session.execute(
            select(CommandPermission).where(CommandPermission.command == command)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = CommandPermission(command=command, roles=roles, permissions=permissions)
            self._session.add(row)
        else:
            row.roles = roles
            row.permissions = permissions
        await self._session.commit()
        await self._session.refresh(row)
        return CommandPermissionEntity(command=row.command, roles=row.roles or [], permissions=row.permissions or [])

